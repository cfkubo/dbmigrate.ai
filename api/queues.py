import pika
import os
import time
import logging
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

QUEUE_CONFIG = {
    object_type: {
        'queue': f"{object_type.lower()}_extraction_jobs",
        'dlx': f"{object_type.lower()}_extraction_dlx",
        'dlq': f"{object_type.lower()}_extraction_dlq",
    }
    for object_type in ['TABLE', 'VIEW', 'PROCEDURE', 'FUNCTION', 'INDEX', 'PACKAGE', 'TRIGGER']
}

QUEUE_CONFIG['SQL_EXECUTION'] = {
    'queue': 'sql_execution_jobs',
    'dlx': 'sql_execution_dlx',
    'dlq': 'sql_execution_dlq',
}

QUEUE_CONFIG['SQL_CONVERSION'] = {
    'queue': 'conversion_jobs',
    'dlx': 'conversion_dlx',
    'dlq': 'conversion_dlq',
}


QUEUE_CONFIG['DATA_MIGRATION_ROW'] = {
    'queue': 'data_migration_row_jobs',
    'dlx': 'data_migration_row_dlx',
    'dlq': 'data_migration_row_dlq',
}

QUEUE_CONFIG['PDF_PROCESSING'] = {
    'queue': 'pdf_processing_jobs',
    'dlx': 'pdf_processing_dlx',
    'dlq': 'pdf_processing_dlq',
}

QUEUE_CONFIG['DATA_MIGRATION_ROW_INSERTS'] = {
    'queue': 'data_migration_row_inserts',
    'dlx': 'data_migration_row_inserts_dlx',
    'dlq': 'data_migration_row_inserts_dlq',
}

QUEUE_CONFIG['DATA_MIGRATION_ROW_INSERTS_DDL'] = {
    'queue': 'data_migration_row_inserts_ddl',
    'dlx': 'data_migration_row_inserts_ddl_dlx',
    'dlq': 'data_migration_row_inserts_ddl_dlq',
}

def get_rabbitmq_connection(retries=5, delay=5):
    """
    Establishes a blocking connection to RabbitMQ with retry logic.
    """
    attempt = 0
    while attempt < retries:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST", "localhost"))
            )
            logger.info("Successfully connected to RabbitMQ.")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            attempt += 1
            logger.error(f"Failed to connect to RabbitMQ on attempt {attempt}/{retries}: {e}")
            if attempt < retries:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
    
    logger.error("Could not connect to RabbitMQ after several retries.")
    return None

def declare_quorum_queue(channel, queue_name, dlx_name):
    try:
        logger.info(f"Declaring DLX exchange: {dlx_name}")
        channel.exchange_declare(exchange=dlx_name, exchange_type='fanout')
        
        dlq_name = f"{queue_name}_dlq"
        logger.info(f"Declaring DLQ for {queue_name}: {dlq_name}")
        channel.queue_declare(queue=dlq_name, durable=True, arguments={'x-queue-type': 'quorum'})
        
        logger.info(f"Binding DLQ {dlq_name} to DLX {dlx_name}")
        channel.queue_bind(exchange=dlx_name, queue=dlq_name)
        
        logger.info(f"Declaring main queue: {queue_name}")
        channel.queue_declare(
            queue=queue_name,
            durable=True,
            arguments={
                'x-queue-type': 'quorum',
                'x-dead-letter-exchange': dlx_name
            }
        )
        logger.info(f"Successfully declared queue and DLQ for {queue_name}")
    except Exception as e:
        logger.error(f"Error declaring quorum queue {queue_name}: {e}")
        raise
def publish_message(queue_name, message):
    """Publishes a message to a specified queue."""
    connection = get_rabbitmq_connection()
    if connection:
        try:
            channel = connection.channel()

            # Inject current trace context into message properties
            carrier = {}
            TraceContextTextMapPropagator().inject(carrier)
            properties = pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                headers=carrier  # Add trace context to headers
            )

            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message,
                properties=properties)
            logger.info(f"Message published to queue: {queue_name}")
        except Exception as e:
            logger.error(f"Failed to publish message to queue {queue_name}: {e}")
        finally:
            connection.close()