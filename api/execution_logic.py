from opentelemetry import trace
from . import database
from . import queues
import pika
import json
from . import sanitizer
from .models import MigrationDetails # Import MigrationDetails
from . import job_repository # Import job_repository
import uuid # Import uuid for generating job IDs

tracer = trace.get_tracer(__name__)

def process_sql_file(file_content: str, filename: str, pg_creds: dict, rabbitmq_connection, is_verification: bool = False) -> str:
    """Sanitizes SQL, creates a job, and publishes it to RabbitMQ with credentials."""
    with tracer.start_as_current_span("process_sql_file"):
        sanitized_sql_statements = sanitizer.sanitize_for_execution(file_content)
        print(f"[API] Sanitized SQL Statements (first 5): {sanitized_sql_statements[:5]}")
        sanitized_sql_string = ";\n".join(sanitized_sql_statements)
        job_id = database.create_sql_execution_job(filename, sanitized_sql_string)

        try:
            if not rabbitmq_connection or not rabbitmq_connection.is_open:
                raise RuntimeError("RabbitMQ connection is not available.")
            
            channel = rabbitmq_connection.channel()
            config = queues.QUEUE_CONFIG['SQL_EXECUTION']
            
            message_body = {
                'job_id': job_id,
                'pg_creds': pg_creds,
                'sanitized_sql_statements': sanitized_sql_statements, # Pass the list of statements
                'is_verification': is_verification # New flag
            }

            channel.basic_publish(
                exchange='',
                routing_key=config['queue'],
                body=json.dumps(message_body),
                properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
            )
            channel.close()
            return job_id
        except pika.exceptions.AMQPError as e:
            # If publishing fails, update the job status to 'failed'
            database.update_sql_execution_job_status(job_id, 'failed', f"Failed to publish to RabbitMQ: {e}")
            raise RuntimeError(f"Failed to publish message to RabbitMQ: {e}") from e

async def initiate_migration_pipeline(migration_details: MigrationDetails) -> str:
    """Initiates the Oracle to PostgreSQL migration pipeline."""
    with tracer.start_as_current_span("initiate_migration_pipeline"):
        # 1. Create a parent migration job
        parent_job_id = job_repository.create_job(
            original_sql=f"Migration of {len(migration_details.selected_objects)} objects from {migration_details.source_schema}",
            job_type="parent_migration"
        )
        print(f"[Migration Pipeline] Initiating migration with Parent Job ID: {parent_job_id}")
        print(f"[Migration Pipeline] Details: {migration_details.json()}")

        # 2. Iterate through selected objects and create child jobs
        for obj in migration_details.selected_objects:
            object_type = obj.object_type.upper()
            object_name = obj.object_name

            # Create a child job for extraction
            child_job_id = job_repository.create_extraction_job(
                parent_job_id=parent_job_id,
                object_type=object_type,
                object_name=object_name,
                source_schema=migration_details.source_schema
            )

            # Publish message to the appropriate extraction queue
            queue_config = queues.QUEUE_CONFIG.get(object_type)
            if not queue_config:
                print(f"Warning: No queue configured for object type: {object_type}. Skipping.")
                job_repository.update_extraction_job_status(child_job_id, "FAILED", error_message=f"No queue configured for object type: {object_type}")
                continue

            message_body = {
                'job_id': child_job_id,
                'parent_job_id': parent_job_id,
                'source_connection': migration_details.source_connection.dict(),
                'target_connection': migration_details.target_connection.dict(),
                'source_schema': migration_details.source_schema,
                'target_schema': migration_details.target_schema,
                'object_type': object_type,
                'object_name': object_name,
                'data_migration_enabled': migration_details.data_migration_enabled and (object_type == 'TABLE')
            }

            try:
                queues.publish_message(queue_config['queue'], json.dumps(message_body))
                job_repository.update_extraction_job_status(child_job_id, "QUEUED")
            except Exception as e:
                print(f"Error publishing message for object {object_name} ({object_type}): {e}")
                job_repository.update_extraction_job_status(child_job_id, "FAILED", error_message=str(e))

        # For now, just return the parent_job_id
        return parent_job_id
