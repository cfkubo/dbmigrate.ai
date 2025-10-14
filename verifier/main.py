
from dotenv import load_dotenv

load_dotenv()
import time

import psycopg2
import os
import sys

# Add the parent directory to the Python path to allow importing the 'api' module.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import database, ai_converter, verification



def process_job(job):
    """Processes a single conversion job."""
    print(f"Processing job: {job['job_id']}")
    try:
        converted_sql = job['converted_sql']

        # Verify the converted SQL
        is_valid, error_message, _ = verification.verify_procedure(converted_sql)

        if is_valid:
            print(f"Job {job['job_id']} verified successfully.")
            database.update_job_status(job['job_id'], 'verified', converted_sql=converted_sql)
        else:
            print(f"Job {job['job_id']} failed verification: {error_message}")
            database.update_job_status(job['job_id'], 'failed', converted_sql=converted_sql, error_message=error_message)

    except Exception as e:
        print(f"An unexpected error occurred while processing job {job['job_id']}: {e}")
        database.update_job_status(job['job_id'], 'failed', error_message=str(e))

def main():
    """The main loop for the verifier process."""
    print("Starting verifier...")

    # --- Database and User Setup ---
    # Ensure the database and user exist before trying to connect as the app user.
    # This mirrors the logic in `api/startup.py` for standalone script resilience.
    try:
        print("Ensuring database and user exist...")
        admin_user = os.getenv("POSTGRES_USER", "postgres")
        admin_password = os.getenv("POSTGRES_PASSWORD", "password")
        db_host = os.getenv("POSTGRES_HOST", "localhost")
        db_port = os.getenv("POSTGRES_PORT", "5432")
        app_db = os.getenv("APP_POSTGRES_DB", "migration_jobs")
        app_user = os.getenv("APP_POSTGRES_USER", "migration_jobs")
        app_password = os.getenv("APP_POSTGRES_PASSWORD", "password")

        database.create_postgres_database(
            host=db_host, port=db_port, user=admin_user, password=admin_password, dbname_to_create=app_db
        )
        database.create_user_if_not_exists(
            host=db_host, port=db_port, admin_user=admin_user, admin_password=admin_password, user_to_create=app_user, password_for_new_user=app_password
        )
        print("Database and user setup verified.")
    except Exception as e:
        print(f"FATAL: Could not initialize database and user. Please check admin credentials and PostgreSQL connection. Error: {e}")
        sys.exit(1)
    # --- End Setup ---

    print("Initializing schema...")
    with database.get_db_connection() as conn:
        database.execute_sql_from_file(conn, "sql-assets/migration_jobs_schema.sql")

    while True:
        jobs = database.get_verified_by_worker_jobs()
        if not jobs:
            print("No pending jobs found. Waiting...")
            time.sleep(10)
            continue

        for job in jobs:
            process_job(job)

if __name__ == "__main__":
    main()
