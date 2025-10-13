
import pika
import os
from dotenv import load_dotenv

load_dotenv()

def reprocess_dlq(dlq_name, target_queue):
    """
    Consumes messages from a DLQ and re-publishes them to the target queue.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters(os.getenv('RABBITMQ_HOST', 'localhost')))
    channel = connection.channel()

    print(f"Checking DLQ: {dlq_name}")
    
    method_frame, header_frame, body = channel.basic_get(dlq_name)
    
    while method_frame:
        print(f"Reprocessing message from {dlq_name}")
        
        headers = header_frame.headers or {}
        retry_count = headers.get('x-retry-count', 0)
        
        if retry_count < 3:
            headers['x-retry-count'] = retry_count + 1
            
            channel.basic_publish(
                exchange='',
                routing_key=target_queue,
                body=body,
                properties=pika.BasicProperties(
                    headers=headers,
                    delivery_mode=2,  # make message persistent
                )
            )
            channel.basic_ack(method_frame.delivery_tag)
            print(f"Message re-queued to {target_queue} with retry count {retry_count + 1}")
        else:
            print(f"Message from {dlq_name} has reached max retries. Discarding.")
            channel.basic_ack(method_frame.delivery_tag)

        method_frame, header_frame, body = channel.basic_get(dlq_name)

    print(f"DLQ {dlq_name} is empty.")
    connection.close()

if __name__ == '__main__':
    reprocess_dlq('sql_conversion_dlq', 'conversion_jobs')
    reprocess_dlq('data_migration_dlq', 'data_migration_jobs')
    reprocess_dlq('conversion_dlq', 'conversion_jobs')
    reprocess_dlq('data_migration_row_inserts_ddl_dlq', 'data_migration_row_inserts_ddl')
