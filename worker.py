from dotenv import load_dotenv

load_dotenv()

import pika
import json
import time
import sys
import os
import psycopg2
import oracledb
import uuid
import sqlparse
from typing import Optional
from contextlib import contextmanager

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace
from opentelemetry.context import attach, detach
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

LoggingInstrumentor().instrument()
RequestsInstrumentor().instrument()
Psycopg2Instrumentor().instrument()

import redis

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(otelTraceID)s - %(otelSpanID)s - %(message)s')
logger = logging.getLogger(__name__)



# Initialize Valkey client
valkey_client = redis.Redis(host='localhost', port=6379, db=0)

# --- FIX 2: Import ThreadPoolExecutor for parallel processing ---
# No longer needed as we are moving to a dedicated consumer for DDL jobs
# from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

WORKER_ID = str(uuid.uuid4())[:8]
from api import database, queues, ai_converter, migration_db, schema_comparer, verification, oracle_helper, job_repository, models
from api.database import get_db_connection, get_verification_db_connection # Import new context managers
from api.verification import verify_procedure, verify_procedure_with_creds

# --- Tracing Setup ---
service_name = "spf-converter-worker"
resource = Resource.create(attributes={
    "service.name": service_name,
    "service.instance.id": f"worker-{WORKER_ID}"
})
provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"))
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# --- REMOVED: Global ThreadPoolExecutor for DDL job processing ---
# executor = ThreadPoolExecutor(max_workers=5)

# --- Existing SQL Conversion Feature ---

SQL_CONVERSION_DLX = 'dlx'
SQL_CONVERSION_DLQ = 'sql_conversion_dlq'
SQL_CONVERSION_QUEUE = 'conversion_jobs'



def sql_conversion_callback(ch, method, properties, body):
    database.initialize_db_pool()
    database.initialize_verification_db_pool()

    data = json.loads(body)
    job_id = data['job_id']
    parent_job_id = data.get('parent_job_id', data['job_id'])
    original_sql = data['original_sql']
    job_type = data.get('job_type', 'spf')
    source_connection_details = data.get('source_connection')
    target_connection_details = data.get('target_connection')
    source_schema = data.get('source_schema')
    target_schema = data.get('target_schema')
    object_name = data.get('object_name')
    data_migration_enabled = data.get('data_migration_enabled')

    # Extract trace context from message properties
    carrier = properties.headers if properties.headers else {}
    ctx = TraceContextTextMapPropagator().extract(carrier)
    token = attach(ctx)

    try:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f" [x] Received {job_type} conversion job {job_id}. Message acknowledged.")

        with tracer.start_as_current_span(f"{job_type}_conversion_job", context=ctx) as span:
            span.set_attribute("job.id", job_id)
            span.set_attribute("parent.job.id", parent_job_id)
            span.set_attribute("job.type", job_type)
            logger.info(f" [x] Starting conversion for job {job_id}")

            database.update_job_status(job_id, 'processing')

            source_db_type = data.get('source_db_type', 'oracle') # Default to oracle for backward compatibility
            converted_sql_chunks = ai_converter.convert_ddl(original_sql, source_db_type, "postgres")
            converted_sql = "".join(converted_sql_chunks)

            # Verification using target connection details
            if target_connection_details:
                success, error_message, verification_results = verification.verify_procedure_with_creds(
                    [converted_sql], # verify_procedure_with_creds expects a list of statements
                    target_connection_details
                )
            else:
                success = True
                error_message = None
                verification_results = None
                logger.warning(f" [!] Job {job_id}: No target connection details provided. Skipping verification.")

            if not success:
                logger.error(f" [!] Job {job_id}: Verification failed: {error_message}. Attempting self-correction.")
                correction_prompt = f"The following PostgreSQL code failed with the error: {error_message}. Please fix it.\n\n{converted_sql}"
                corrected_sql = "".join(ai_converter.convert_ddl(correction_prompt, source_db_type, "postgres"))
                
                success, error_message, verification_results = verification.verify_procedure_with_creds(
                    [corrected_sql],
                    target_connection_details
                )
                if success:
                    converted_sql = corrected_sql

            if success and not error_message:
                final_status = 'verified_by_worker'
                logger.info(f" [x] {job_type.upper()} Job {job_id}: Verification by worker successful.")
                span.set_status(trace.Status(trace.StatusCode.OK))
                job_repository.update_job_status(job_id, final_status, original_sql=original_sql, converted_sql=converted_sql)
            else:
                final_status = 'failed'
                logger.error(f" [!] {job_type.upper()} Job {job_id}: Verification failed: {error_message}")
                span.set_status(trace.Status(trace.StatusCode.ERROR, f"Verification failed: {error_message}"))
                job_repository.update_job_status(job_id, final_status, original_sql=original_sql, converted_sql=converted_sql, error_message=error_message)

    except Exception as e: # Critical error in callback
        error_message = f"Critical error in sql_conversion_callback for job {job_id}: {e}"
        logger.error(error_message, exc_info=True)
        # Ensure original_sql is preserved even on critical failure
        existing_job = job_repository.get_job(job_id)
        current_original_sql = existing_job.get('original_sql') if existing_job else None
        job_repository.update_job_status(job_id, 'failed', original_sql=current_original_sql, error_message=error_message)
        span.set_status(trace.Status(trace.StatusCode.ERROR, f"Critical failure: {error_message}"))
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True) # Requeue for retry
    finally:
        detach(token)

# def callback(ch, method, properties, body):
def sql_execution_callback(ch, method, properties, body):
    database.initialize_db_pool()
    database.initialize_verification_db_pool() # Initialize verification pool as well
    data = json.loads(body)
    job_id = data['job_id']
    parent_job_id = data.get('parent_job_id')
    pg_creds = data.get('pg_creds')
    sanitized_sql_statements = data.get('sanitized_sql_statements')
    is_verification = data.get('is_verification', False)
    object_type = data.get('object_type')
    object_name = data.get('object_name')
    source_schema = data.get('source_schema')
    target_schema = data.get('target_schema')
    data_migration_enabled = data.get('data_migration_enabled', False)

    print(f"[Worker] Received SQL Statements (first 5): {sanitized_sql_statements[:5]}")

    # Extract trace context from message properties
    carrier = properties.headers if properties.headers else {}
    ctx = TraceContextTextMapPropagator().extract(carrier)
    token = attach(ctx)

    MAX_RETRIES = 3
    retry_count = 0
    if properties.headers and 'x-death' in properties.headers:
        for death_entry in properties.headers['x-death']:
            if death_entry['queue'] == queues.QUEUE_CONFIG['SQL_EXECUTION']['queue']:
                retry_count = death_entry['count']
                break

    try:
        with tracer.start_as_current_span("sql_execution_job", context=ctx) as span:
            span.set_attribute("job.id", job_id)
            span.set_attribute("parent.job.id", parent_job_id)
            span.set_attribute("job.type", "sql_execution")
            span.set_attribute("object.type", object_type)
            span.set_attribute("object.name", object_name)
            print(f" [x] Received SQL execution job {job_id} (Retry: {retry_count})")
            job = database.get_sql_execution_job(job_id)
            if not job:
                raise ValueError("Job not found in database")

            if retry_count >= MAX_RETRIES:
                final_error_message = f"SQL execution failed after {MAX_RETRIES} retries. Last error: {job.get('error_message', 'Unknown error')}"
                print(f" [!] Job {job_id}: Retry limit exceeded. {final_error_message}")
                database.update_sql_execution_job_status(job_id, 'failed', final_error_message, job.get('statement_results', []))
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            database.update_sql_execution_job_status(job_id, 'processing')

            overall_success = True
            overall_error_message = None
            statement_results = []

            # Determine which connection to use
            if is_verification:
                print(f" [x] Job {job_id}: Using verification database for execution.")
                with get_verification_db_connection() as conn:
                    overall_success, overall_error_message, statement_results = verification.verify_procedure(sanitized_sql_statements)
            elif pg_creds:
                print(f" [x] Job {job_id}: Using provided credentials for execution.")
                overall_success, overall_error_message, statement_results = verification.verify_procedure_with_creds(sanitized_sql_statements, pg_creds)
            else:
                print(f" [x] Job {job_id}: Using default database for execution.")
                with get_db_connection() as conn:
                    overall_success, overall_error_message, statement_results = verification.verify_procedure(sanitized_sql_statements)

            if overall_success:
                print(f"Job {job_id} executed successfully.")
                database.update_sql_execution_job_status(job_id, 'verified', None, statement_results)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                span.set_status(trace.Status(trace.StatusCode.OK))

                # --- Conditional Data Migration --- #
                if object_type == 'TABLE' and data_migration_enabled:
                    logger.info(f" [x] DDL for table {object_name} executed successfully. Initiating data migration for job {job_id}.")
                    # Create a data migration job
                    data_mig_job_id = database.create_data_migration_job(
                        source_db_type="Oracle",
                        source_connection_string=json.dumps(data['source_connection']),
                        source_schema_name=source_schema,
                        source_table_name=object_name,
                        target_db_type="PostgreSQL",
                        target_connection_string=json.dumps(pg_creds),
                        target_schema_name=target_schema,
                        target_table_name=object_name # Assuming target table name is same as source
                    )
                    logger.info(f" [x] Data migration job {data_mig_job_id} created for table {object_name}.")

                    # Fetch data from Oracle and publish to data_migration_row_inserts queue
                    try:
                        oracle_column_names, oracle_rows = oracle_helper.fetch_oracle_table_data_batched(
                            data['source_connection'],
                            source_schema,
                            object_name
                        )
                        logger.info(f"Extracted {len(oracle_rows)} rows from Oracle table {source_schema}.{object_name}")

                        for i, row_data in enumerate(oracle_rows):
                            message = {
                                "job_id": str(data_mig_job_id),
                                "row_number": i + 1,
                                "row_data": list(row_data), # Convert tuple to list for JSON serialization
                                "column_names": oracle_column_names
                            }
                            queues.publish_message(queues.QUEUE_CONFIG['DATA_MIGRATION_ROW_INSERTS']['queue'], json.dumps(message))
                        
                        database.update_data_migration_job_status(data_mig_job_id, "IN_PROGRESS", total_rows=len(oracle_rows))
                        logger.info(f"Published {len(oracle_rows)} raw row messages to RabbitMQ for data migration job {data_mig_job_id}.")

                    except Exception as e:
                        logger.error(f"Error during data extraction or publishing for job {data_mig_job_id}: {e}", exc_info=True)
                        database.update_data_migration_job_status(data_mig_job_id, "FAILED", error_details=str(e))

            else:
                print(f" [!] Job {job_id} failed execution: {overall_error_message}. Re-queueing for retry.")
                database.update_sql_execution_job_status(job_id, 'failed', overall_error_message, statement_results) # Update with current failure details
                ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True) # Re-queue for retry
                span.set_status(trace.Status(trace.StatusCode.ERROR, f"Execution failed: {overall_error_message}"))

    except Exception as e:
        print(f" [!] Job {job_id} failed critically: {e}. Re-queueing for retry.")
        database.update_sql_execution_job_status(job_id, 'failed', str(e), statement_results if 'statement_results' in locals() else [])
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True) # Re-queue for retry)
        span.set_status(trace.Status(trace.StatusCode.ERROR, f"Critical failure: {e}"))
    finally:
        detach(token)


# --- PDF Processing Feature ---

def pdf_processing_callback(ch, method, properties, body):
    database.initialize_db_pool()
    rag_service = RAGService() # Instantiate RAGService
    data = json.loads(body)
    document_id = data['document_id']
    filename = data['filename']
    user_id = data['user_id']
    temp_file_path = data['temp_file_path']

    # Extract trace context from message properties
    carrier = properties.headers if properties.headers else {}
    ctx = TraceContextTextMapPropagator().extract(carrier)
    token = attach(ctx)

    try:
        with tracer.start_as_current_span("pdf_processing_job", context=ctx) as span:
            span.set_attribute("document.id", document_id)
            span.set_attribute("filename", filename)
            span.set_attribute("user.id", user_id)
            print(f" [x] Received PDF processing job for document {document_id} (file: {filename})")

            # Extract text from PDF
            pages_content = rag_service.extract_text_from_pdf(temp_file_path)

            # Process each page
            for page_data in pages_content:
                full_page_text = page_data['content']

                # Chunk the text
                chunks = rag_service.chunk_text(full_page_text)

                # Generate embeddings and store each chunk
                for chunk in chunks:
                    embedding = rag_service.generate_embeddings(chunk)
                    database.insert_document_chunk(
                        document_id=document_id,
                        text=chunk,
                        embedding=embedding,
                        embedding_model=rag_service.embedding_model_name,
                        llm_model=rag_service.llm_model_name
                    )

            # Update document status to completed
            database.update_document_status(
                document_id,
                "completed",
                embedding_model=rag_service.embedding_model_name,
                llm_model=rag_service.llm_model_name
            )
            print(f" [x] Processed PDF document {document_id} successfully.")
            span.set_status(trace.Status(trace.StatusCode.OK))
            ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        error_message = f"Failed to process PDF document {document_id}: {e}"
        print(f" [!] {error_message}")
        database.update_document_status(document_id, "failed", error_message)
        span.set_status(trace.Status(trace.StatusCode.ERROR, f"PDF processing failed: {error_message}"))
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        detach(token)
# --- FIX 3: Add placeholder for data_migration_row_callback ---
def data_migration_row_callback(ch, method, properties, body):
    # TODO: Implement actual data migration row logic here
    # Extract trace context from message properties
    carrier = properties.headers if properties.headers else {}
    ctx = TraceContextTextMapPropagator().extract(carrier)
    token = attach(ctx)

    try:
        with tracer.start_as_current_span("data_migration_row_job", context=ctx) as span:
            span.set_attribute("job.type", "data_migration_row")
            print(f" [x] Received Data Migration Row job: {body}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            span.set_status(trace.Status(trace.StatusCode.OK))
    except Exception as e:
        print(f" [!] Error processing Data Migration Row job: {e}")
        span.set_status(trace.Status(trace.StatusCode.ERROR, f"Data migration row job failed: {e}"))
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True) # Requeue for retry
    finally:
        detach(token)

# --- New: Callback for data_migration_row_inserts queue ---
def data_migration_row_inserts_callback(ch, method, properties, body):
    database.initialize_db_pool()
    data = json.loads(body)
    job_id = data['job_id']
    row_number = data['row_number']
    row_data = data['row_data']
    column_names = data['column_names']

    # Extract trace context from message properties
    carrier = properties.headers if properties.headers else {}
    ctx = TraceContextTextMapPropagator().extract(carrier)
    token = attach(ctx)

    try:
        with tracer.start_as_current_span("data_migration_row_inserts_job", context=ctx) as span:
            span.set_attribute("job.id", job_id)
            span.set_attribute("row.number", row_number)
            span.set_attribute("job.type", "data_migration_row_inserts")
            print(f" [x] Received data_migration_row_inserts job for job_id: {job_id}, row_number: {row_number}")
            migration_db.process_row_for_insertion(job_id, row_data, column_names)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            span.set_status(trace.Status(trace.StatusCode.OK))
    except Exception as e:
        print(f" [!] Error processing data_migration_row_inserts job for job_id {job_id}, row_number {row_number}: {e}")
        span.set_status(trace.Status(trace.StatusCode.ERROR, f"Data migration row inserts failed: {e}"))
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True) # Requeue for retry
    finally:
        detach(token)

# --- New: Callback for data_migration_row_inserts_ddl queue ---
def data_migration_row_inserts_ddl_callback(ch, method, properties, body):
    database.initialize_db_pool()
    data = json.loads(body)
    job_id = data['job_id']
    ddl_statement = data['ddl_statement']

    # Extract trace context from message properties
    carrier = properties.headers if properties.headers else {}
    ctx = TraceContextTextMapPropagator().extract(carrier)
    token = attach(ctx)

    try:
        with tracer.start_as_current_span("data_migration_row_inserts_ddl_job", context=ctx) as span:
            span.set_attribute("job.id", job_id)
            span.set_attribute("job.type", "data_migration_row_inserts_ddl")
            print(f" [x] Received data_migration_row_inserts_ddl job for job_id: {job_id}")
            migration_db.execute_ddl_statement(job_id, ddl_statement)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            span.set_status(trace.Status(trace.StatusCode.OK))
    except Exception as e:
        print(f" [!] Error processing data_migration_row_inserts_ddl job for job_id {job_id}: {e}")
        span.set_status(trace.Status(trace.StatusCode.ERROR, f"Data migration row inserts DDL failed: {e}"))
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True) # Requeue for retry
    finally:
        detach(token)

# --- New: Extraction Callback ---
def extraction_callback(ch, method, properties, body):
    database.initialize_db_pool()
    data = json.loads(body)
    job_id = data['job_id']
    parent_job_id = data['parent_job_id']
    source_connection_details = data['source_connection']
    object_type = data['object_type']
    object_name = data['object_name']
    source_schema = data['source_schema']
    target_schema = data['target_schema']
    data_migration_enabled = data['data_migration_enabled']

    # Convert source_connection_details dictionary to OracleConnectionDetails object
    oracle_details = models.OracleConnectionDetails(**source_connection_details)

    # Extract trace context from message properties
    carrier = properties.headers if properties.headers else {}
    ctx = TraceContextTextMapPropagator().extract(carrier)
    token = attach(ctx)

    try:
        with tracer.start_as_current_span("extraction_job", context=ctx) as span:
            span.set_attribute("job.id", job_id)
            span.set_attribute("parent.job.id", parent_job_id)
            span.set_attribute("object.type", object_type)
            span.set_attribute("object.name", object_name)
            span.set_attribute("job.type", "extraction")
            logger.info(f" [x] Received extraction job for {object_type} {object_name} (Job ID: {job_id})")

            # Update job status to processing
            job_repository.update_job_status(job_id, 'processing')

            extracted_ddl = None
            error_message = None
            try:
                if object_type == 'TABLE':
                    extracted_ddl = oracle_helper.get_oracle_table_ddl(oracle_details, source_schema, object_name)
                elif object_type == 'VIEW':
                    extracted_ddl = oracle_helper.get_oracle_view_ddl(oracle_details, source_schema, object_name)
                elif object_type == 'PROCEDURE':
                    extracted_ddl = oracle_helper.get_oracle_procedure_ddl(oracle_details, source_schema, object_name)
                elif object_type == 'FUNCTION':
                    extracted_ddl = oracle_helper.get_oracle_function_ddl(oracle_details, source_schema, object_name)
                elif object_type == 'INDEX':
                    extracted_ddl = oracle_helper.get_oracle_index_ddl(oracle_details, source_schema, object_name)
                elif object_type == 'PACKAGE':
                    extracted_ddl = oracle_helper.get_oracle_package_ddl(oracle_details, source_schema, object_name)
                elif object_type == 'TRIGGER':
                    extracted_ddl = oracle_helper.get_oracle_trigger_ddl(oracle_details, source_schema, object_name)
                else:
                    error_message = f"Unsupported object type for extraction: {object_type}"
                    logger.error(error_message)

                if not extracted_ddl and not error_message:
                    error_message = f"No DDL extracted for {object_type} {object_name}"
                    logger.warning(error_message)

            except Exception as e:
                error_message = f"Error extracting DDL for {object_type} {object_name}: {e}"
                logger.error(error_message, exc_info=True)

            if extracted_ddl:
                job_repository.update_job_status(job_id, 'extracted', original_sql=extracted_ddl)
                logger.info(f" [x] Successfully extracted DDL for {object_type} {object_name} (Job ID: {job_id})")

                # Publish to SQL_CONVERSION queue
                conversion_message = {
                    'job_id': job_id,
                    'parent_job_id': parent_job_id,
                    'original_sql': extracted_ddl,
                    'job_type': object_type.lower(), # e.g., 'table', 'view'
                    'source_connection': source_connection_details,
                    'target_connection': data['target_connection'],
                    'source_schema': source_schema,
                    'target_schema': target_schema,
                    'object_name': object_name,
                    'data_migration_enabled': data_migration_enabled
                }
                queues.publish_message(queues.QUEUE_CONFIG['SQL_CONVERSION']['queue'], json.dumps(conversion_message))
                span.set_status(trace.Status(trace.StatusCode.OK))
            else:
                job_repository.update_job_status(job_id, 'failed', error_message=error_message)
                span.set_status(trace.Status(trace.StatusCode.ERROR, f"Extraction failed: {error_message}"))

            ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        error_message = f"Critical error in extraction_callback for job {job_id}: {e}"
        logger.error(error_message, exc_info=True)
        job_repository.update_job_status(job_id, 'failed', error_message=error_message)
        span.set_status(trace.Status(trace.StatusCode.ERROR, f"Critical failure: {error_message}"))
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True) # Requeue for retry
    finally:
        detach(token)

    # --- Main Application Setup ---


def main():
    # Defer database initialization to within the callbacks
    logger.info(f"WORKER DB_HOST: {os.getenv('POSTGRES_HOST')}, DB_PORT: {os.getenv('POSTGRES_PORT')}, DB_NAME: {os.getenv('APP_POSTGRES_DB')}")
    connection = pika.BlockingConnection(pika.ConnectionParameters(os.getenv('RABBITMQ_HOST', 'localhost')))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)

    # Map queue keys to their respective callback functions
    callback_map = {
        'SQL_CONVERSION': sql_conversion_callback,
        'DATA_MIGRATION_ROW': data_migration_row_callback,
        'SQL_EXECUTION': sql_execution_callback,
        'PDF_PROCESSING': pdf_processing_callback,
        'DATA_MIGRATION_ROW_INSERTS': data_migration_row_inserts_callback,
        'DATA_MIGRATION_ROW_INSERTS_DDL': data_migration_row_inserts_ddl_callback,
    }

    # Add extraction callbacks dynamically
    for obj_type_key in ['TABLE', 'VIEW', 'PROCEDURE', 'FUNCTION', 'INDEX', 'PACKAGE', 'TRIGGER']:
        callback_map[obj_type_key] = extraction_callback

    # Iterate through QUEUE_CONFIG to declare queues and set up consumers
    for queue_key, config in queues.QUEUE_CONFIG.items():
        queue_name = config['queue']
        dlx_name = config['dlx']

        # Declare the queue and its DLX/DLQ
        queues.declare_quorum_queue(channel, queue_name, dlx_name)

        # Set up consumer if a callback is defined for this queue
        if queue_key in callback_map:
            channel.basic_consume(queue=queue_name, on_message_callback=callback_map[queue_key])
            print(f"[*] Listening for messages on '{queue_name}'.")
        else:
            print(f"[!] No callback defined for queue: {queue_name}. Skipping consumer setup.")

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)