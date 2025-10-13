from fastapi import FastAPI
import pika
from . import database
from . import queues
from . import migration_db
from contextlib import asynccontextmanager
import os
import time
from .database import create_postgres_database, create_user_if_not_exists

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Use the admin user 'postgres' with the password from docker-compose to create DBs and users.
    admin_user = os.getenv("POSTGRES_USER", "postgres")
    admin_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")

    # Retry mechanism for database initialization
    max_retries = 5
    retry_delay = 5  # seconds
    for attempt in range(max_retries):
        try:
            # Create main and verification databases if they don't exist
            if not create_postgres_database(
                host=os.getenv("VERIFICATION_DB_HOST", db_host),
                port=os.getenv("VERIFICATION_DB_PORT", db_port),
                user=admin_user,
                password=admin_password,
                dbname_to_create=os.getenv("VERIFICATION_DB_NAME", "verification_db")
            ):
                raise ConnectionError("Failed to create verification database")

            if not create_postgres_database(
                host=db_host,
                port=db_port,
                user=admin_user,
                password=admin_password,
                dbname_to_create="migration_jobs"
            ):
                raise ConnectionError("Failed to create migration_jobs database")

            # Create the 'migration_jobs' user if it doesn't exist
            if not create_user_if_not_exists(
                host=db_host,
                port=db_port,
                admin_user=admin_user,
                admin_password=admin_password,
                user_to_create="migration_jobs",
                password_for_new_user="password"
            ):
                raise ConnectionError("Failed to create migration_jobs user")



            # Create the 'rag_user' if it doesn't exist


            # Now, initialize the connection pools which may use the 'migration_jobs' user from the .env file
            database.initialize_db_pool()

            database.initialize_verification_db_pool()

            # Grant privileges to the migration_jobs user on the migration_jobs database
            with database.get_db_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("GRANT ALL PRIVILEGES ON DATABASE migration_jobs TO migration_jobs")
                    conn.commit()
                    print("Granted all privileges on database migration_jobs to user migration_jobs.")
                except Exception as e:
                    conn.rollback()
                    print(f"Could not grant privileges: {e}")
                finally:
                    cursor.close()



            try:
                with database.get_db_connection() as conn:
                    print("Applying migration_jobs DB schema...")
                    database.execute_sql_from_file(conn, "sql-assets/migration_jobs_schema.sql")
                    migration_db.migrate_sql_execution_jobs(conn)
                    print("migration_jobs DB schema applied successfully.")

                with database.get_verification_db_connection() as conn:
                    print("Applying verification DB schema...")
                    database.execute_sql_from_file(conn, "sql-assets/verification_schema.sql")
                    print("verification DB schema applied successfully.")


            except Exception as e:
                print(f"An error occurred during schema creation: {e}")
                raise




            # If all successful, break the loop
            print("Database initialization successful.")
            break
        except Exception as e:
            print(f"Database initialization failed on attempt {attempt + 1}/{max_retries}: {e}")
            if attempt + 1 == max_retries:
                print("Max retries reached. Could not initialize database.")
                # Depending on desired behavior, you might want to raise the exception
                # or exit the application. For now, we'll let it proceed and likely fail
                # at the next database operation, which will be caught by FastAPI's startup handling.
                raise
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

    # Declare queues on startup
    print("Attempting to get RabbitMQ connection for queue declaration...")
    connection = queues.get_rabbitmq_connection()
    if connection:
        print("RabbitMQ connection successful. Declaring queues...")
        declare_queues(connection)
        connection.close()
        print("RabbitMQ connection closed after queue declaration.")
    else:
        print("Failed to get RabbitMQ connection. Queues not declared.")

    yield

def declare_queues(connection):
    if not connection:
        print("Cannot declare queues, no RabbitMQ connection.")
        return
    try:
        channel = connection.channel()
        print("Channel opened for queue declaration.")
        for object_type in queues.QUEUE_CONFIG:
            config = queues.QUEUE_CONFIG[object_type]
            queue_name = config['queue']
            dlx_name = config['dlx']
            print(f"Declaring queue: {queue_name} with DLX: {dlx_name}")
            queues.declare_quorum_queue(channel, queue_name, dlx_name)
        channel.close()
        print("Channel closed after queue declaration.")
    except pika.exceptions.AMQPError as e:
        print(f"Failed to declare queues: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during queue declaration: {e}")
