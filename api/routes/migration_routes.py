import logging
from fastapi import APIRouter, HTTPException
import os
import pika
import json
import uuid
from .. import models
from .. import schema_comparer
from ..ai_converter import compare_schemas_with_ollama_ai
from .. import database
from .. import queues
from .. import oracle_helper
from .. import job_repository # Import job_repository directly

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/migrate")
def initiate_migration_workflow(migration_details: models.MigrationDetails):
    logger.info(f"Initiating migration workflow for job: {migration_details.selected_objects}")

    try:
        # 1. Create a parent job in the database
        # This parent job will track the overall migration status
        parent_job_id = job_repository.create_job(
            job_type="migration_workflow",
            source_db_type=migration_details.source_db_type,
            target_db_type=migration_details.target_db_type,
            source_connection_details=migration_details.source_connection.dict(),
            target_connection_details=migration_details.target_connection.dict() if migration_details.target_connection else None,
            source_schema=migration_details.source_schema,
            target_schema=migration_details.target_schema,
            data_migration_enabled=migration_details.data_migration_enabled
        )
        # 2. For each selected object, create a child job (extraction/conversion) and publish to the EXTRACTION_QUEUE
        for obj in migration_details.selected_objects:
            child_job_id = job_repository.create_job(
                job_type=f"{obj.object_type.lower()}_extraction", # e.g., 'table_extraction'
                parent_job_id=parent_job_id,
                object_type=obj.object_type,
                object_name=obj.object_name,
                source_schema=migration_details.source_schema,
                target_schema=migration_details.target_schema,
                source_connection_details=migration_details.source_connection.dict(),
                target_connection_details=migration_details.target_connection.dict() if migration_details.target_connection else None,
                data_migration_enabled=migration_details.data_migration_enabled
            )

            extraction_message = {
                'job_id': child_job_id,
                'parent_job_id': parent_job_id,
                'source_connection': migration_details.source_connection.dict(),
                'target_connection': migration_details.target_connection.dict() if migration_details.target_connection else None,
                'object_type': obj.object_type,
                'object_name': obj.object_name,
                'source_schema': migration_details.source_schema,
                'target_schema': migration_details.target_schema,
                'data_migration_enabled': migration_details.data_migration_enabled
            }
            # Use the dynamically generated queue name for the specific object type
            queues.publish_message(queues.QUEUE_CONFIG[obj.object_type]['queue'], json.dumps(extraction_message))
            logger.info(f"Published extraction job {child_job_id} for {obj.object_type} {obj.object_name}")

        return {"job_id": parent_job_id, "message": "Migration workflow initiated successfully."}
    except Exception as e:
        logger.error(f"Error initiating migration workflow: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error initiating migration workflow: {e}")

@router.post("/migrate/start")
def start_migration(request: models.DataMigrationRequest):
    print("### HELLO FROM START MIGRATION ###")
    if not all([request.oracle_credentials, request.postgres_credentials, request.source_schema, request.source_table, request.destination_schema, request.destination_table]):
        raise HTTPException(status_code=400, detail="All fields are required.")

    # 1. Perform Schema Compatibility Check
    try:
        # Fetch Oracle DDL
        oracle_ddl = oracle_helper.get_oracle_table_ddl(
            request.oracle_credentials,
            request.source_schema,
            request.source_table
        )
        if not oracle_ddl:
            raise HTTPException(status_code=404, detail=f"Oracle DDL not found for table {request.source_table}")

        # Fetch PostgreSQL DDL
        postgres_ddl = database.get_postgres_table_ddl(
            request.destination_schema,
            request.destination_table,
            dbname=request.postgres_credentials.dbname
        )
        if not postgres_ddl:
            raise HTTPException(status_code=404, detail=f"PostgreSQL DDL not found for table {request.destination_table}")

        is_compatible, issues = compare_schemas_with_ollama_ai(
            oracle_ddl=oracle_ddl,
            postgres_ddl=postgres_ddl,
            data_migration_mode=True
        )

        if not is_compatible:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Schema incompatibility detected",
                    "issues": issues
                }
            )
    except Exception as e:
        logger.exception("Schema comparison failed during migration start.")
        raise HTTPException(status_code=500, detail=f"Schema comparison failed: {e}")

    # 2. Create a new migration job in PostgreSQL
    try:
        job_id = database.create_data_migration_job(
            source_db_type="Oracle",
            source_connection_string=json.dumps(request.oracle_credentials.dict()),
            source_schema_name=request.source_schema,
            source_table_name=request.source_table,
            target_db_type="PostgreSQL",
            target_connection_string=json.dumps(request.postgres_credentials.dict()),
            target_schema_name=request.destination_schema,
            target_table_name=request.destination_table
        )
    except Exception as e:
        logger.exception("Failed to create migration job during migration start.")
        raise HTTPException(status_code=500, detail=f"Failed to create migration job: {e}")

    # 3. Extract data from Oracle
    try:
        oracle_column_names, oracle_rows = oracle_helper.fetch_oracle_table_data_batched(
            request.oracle_credentials,
            request.source_schema,
            request.source_table
        )
        logger.info(f"Extracted {len(oracle_rows)} rows from Oracle table {request.source_schema}.{request.source_table}")
    except Exception as e:
        logger.exception("Failed to extract data from Oracle during migration start.")
        database.update_data_migration_job_status(job_id, "FAILED", error_details=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to extract data from Oracle: {e}")

    # 4. Generate PostgreSQL INSERT statements (placeholder for now)
    # This is where we will generate the actual INSERT statements based on oracle_column_names, oracle_rows, and postgres_ddl
    # For now, we'll just log a message.
    logger.info("Placeholder: Generating PostgreSQL INSERT statements...")

    # 4. Publish each Oracle row to RabbitMQ for worker to pick up
    print("DEBUG: Starting Publish to RabbitMQ")
    try:
        connection = queues.get_rabbitmq_connection()
        if not connection:
            raise HTTPException(status_code=500, detail="Failed to connect to RabbitMQ.")
        channel = connection.channel()

        # Declare the queue for row-level inserts if it doesn't exist
        row_insert_queue_name = "data_migration_row_inserts"
        channel.queue_declare(queue=row_insert_queue_name, durable=True, arguments={'x-queue-type': 'quorum', 'x-dead-letter-exchange': 'data_migration_row_inserts_dlx'})

        for i, row_data in enumerate(oracle_rows):
            message = {
                "job_id": str(job_id),
                "row_number": i + 1,
                "row_data": list(row_data), # Convert tuple to list for JSON serialization
                "column_names": oracle_column_names
            }
            channel.basic_publish(
                exchange='',
                routing_key=row_insert_queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2) # make message persistent
            )
        logger.info(f"Published {len(oracle_rows)} raw row messages to RabbitMQ for job {job_id}.")
        connection.close()

        database.update_data_migration_job_status(job_id, "IN_PROGRESS", total_rows=len(oracle_rows))

        return {"job_id": job_id, "message": "Migration job submitted and raw rows queued successfully."}
    except Exception as e:
        logger.exception("Error submitting migration job to queue during migration start.")
        database.update_data_migration_job_status(job_id, "FAILED", error_details=str(e))
        raise HTTPException(status_code=500, detail=f"Error submitting migration job to queue: {e}")

@router.get("/migration/status/{job_id}")
def get_migration_status(job_id: str):
    if not job_id:
        raise HTTPException(status_code=400, detail="Job ID is required.")
    try:
        parent_job = database.get_job(job_id)
        if not parent_job:
            raise HTTPException(status_code=404, detail="Parent migration job not found.")

        child_jobs_status = database.get_all_child_job_statuses(job_id)

        # Aggregate child job statuses into a more consumable format for the frontend
        # This structure should match what the frontend's MigrationPipelines.js expects
        aggregated_child_status = []
        for child_job in child_jobs_status:
            # Determine the stage based on the table it came from
            stage = child_job["stage"]
            
            aggregated_child_status.append({
                "job_id": str(child_job["job_id"]),
                "object_type": child_job.get("object_type", "unknown"),
                "object_name": child_job.get("object_name", child_job.get("source_table_name", "unknown")),
                "stage": stage,
                "status": child_job["status"],
                "error_message": child_job.get("error_message") or child_job.get("error_details"),
                "extracted_ddl": child_job.get("extracted_ddl"),
                "converted_ddl": child_job.get("converted_sql"),
                # Add other relevant fields as needed by the frontend
            })

        return {
            "job_id": str(parent_job["job_id"]),
            "status": parent_job["status"],
            "error_message": parent_job.get("error_message"),
            "child_jobs": aggregated_child_status
        }
    except Exception as e:
        logger.error(f"Error checking migration job status for {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error checking migration job status: {e}")

@router.post("/oracle/schemas")
def get_oracle_schemas_route(details: models.OracleConnectionDetails):
    try:
        schemas = oracle_helper.get_oracle_schemas(details)
        return {"schemas": schemas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Oracle schemas: {e}")

@router.post("/oracle/schemas/{schema_name}/tables")
def list_oracle_tables_route(schema_name: str, details: models.OracleConnectionDetails):
    try:
        tables = oracle_helper.list_oracle_objects(details, schema_name, "TABLE")
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Oracle tables for schema {schema_name}: {e}")

@router.post("/postgres/schemas")
def get_postgres_schemas_route(details: models.PostgresConnectionDetails = None):
    try:
        dbname = details.dbname if details else None
        schemas = database.get_postgres_schemas(dbname=dbname)
        return {"schemas": schemas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching PostgreSQL schemas: {e}")

@router.post("/postgres/schemas/{schema_name}/tables")
def list_postgres_tables_route(schema_name: str, details: models.PostgresConnectionDetails = None):
    try:
        dbname = details.dbname if details else None
        tables = database.list_postgres_tables(schema_name, dbname=dbname)
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching PostgreSQL tables for schema {schema_name}: {e}")

@router.post("/oracle/schemas/{schema_name}/tables/{table_name}/ddl")
def get_oracle_table_ddl_route(schema_name: str, table_name: str, details: models.OracleConnectionDetails):
    try:
        ddl = oracle_helper.get_oracle_table_ddl(details, schema_name, table_name)
        if ddl:
            return {"ddl": ddl}
        raise HTTPException(status_code=404, detail="DDL not found for the specified table.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Oracle DDL: {e}")

@router.post("/postgres/schemas/{schema_name}/tables/{table_name}/ddl")
def get_postgres_table_ddl_route(schema_name: str, table_name: str, details: models.PostgresConnectionDetails = None):
    try:
        dbname = details.dbname if details else None
        ddl = database.get_postgres_table_ddl(schema_name, table_name, dbname=dbname)
        if ddl:
            return {"ddl": ddl}
        raise HTTPException(status_code=404, detail="DDL not found for the specified table.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching PostgreSQL DDL: {e}")
