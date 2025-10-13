import psycopg2
import os
from dotenv import load_dotenv
import json
from . import database # Import the database module

load_dotenv()

def migrate_sql_execution_jobs(conn=None):
    """
    Migrates the sql_execution_jobs table to a new schema.
    - Renames the old table to sql_execution_jobs_old.
    - Creates a new sql_execution_jobs table with the correct schema.
    - Copies data from the old table to the new one.
    - (Optional) Deletes the old table.
    """
    conn = None
    close_conn = False
    if conn is None:
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB", "migration_jobs"),
                user=os.getenv("POSTGRES_USER", "migration_jobs"),
                password=os.getenv("POSTGRES_PASSWORD", "password"),
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=os.getenv("POSTGRES_PORT", "5432"),
            )
            close_conn = True
            conn.autocommit = True
            cursor = conn.cursor()

            # Add the 'statement_results' column if it doesn't exist
            cursor.execute("""
                ALTER TABLE migration_jobs.sql_execution_jobs
                ADD COLUMN IF NOT EXISTS statement_results JSONB;
            """)
            print("Ensured 'statement_results' column exists in sql_execution_jobs.")

            cursor.close()
            print("Migration completed successfully.")

        except psycopg2.Error as e:
            print(f"Error during migration: {e}")
        finally:
            if close_conn and conn:
                conn.close()
                print("Database connection closed.")
    else:
        print("Connection provided, skipping connection setup.")

def process_row_for_insertion(job_id: str, row_data: list, column_names: list):
    job = database.get_data_migration_job(job_id)
    if not job:
        raise ValueError(f"Migration job with ID {job_id} not found.")

    target_connection_string = json.loads(job["target_connection_string"])
    target_schema = job["target_schema_name"]
    target_table = job["target_table_name"]

    # Get actual PostgreSQL column names
    pg_column_names = database.get_postgres_table_column_names(
        schema_name=target_schema,
        table_name=target_table,
        dbname=target_connection_string["dbname"]
    )

    if not pg_column_names:
        raise ValueError(f"No columns found for target table {target_schema}.{target_table}")

    # Create a mapping from Oracle column names (case-insensitive) to actual PostgreSQL column names
    oracle_col_map = {col.lower(): col for col in column_names}
    pg_col_map = {col.lower(): col for col in pg_column_names}

    insert_cols_for_pg = []
    values_for_pg = []

    for oracle_col_original in column_names:
        oracle_col_lower = oracle_col_original.lower()
        if oracle_col_lower in pg_col_map:
            # Use the actual PostgreSQL column name, and ensure it's quoted
            insert_cols_for_pg.append(f'"{pg_col_map[oracle_col_lower]}"')
            # Find the index of the original Oracle column name to get the correct value
            original_oracle_index = column_names.index(oracle_col_original)
            values_for_pg.append(row_data[original_oracle_index])
        else:
            # Log a warning if an Oracle column doesn't have a matching PostgreSQL column
            print(f"[WARNING] Oracle column '{oracle_col_original}' not found in target PostgreSQL table '{target_schema}.{target_table}'. Skipping.")

    if not insert_cols_for_pg:
        raise ValueError(f"No matching columns found between source and target for job {job_id}.")

    # Construct the INSERT statement with correctly quoted PostgreSQL column names
    insert_sql = f"INSERT INTO \"{target_schema}\".\"{target_table}\" ({', '.join(insert_cols_for_pg)}) VALUES ({', '.join(['%s'] * len(values_for_pg))})"

    with database.get_db_connection_by_db_name(
        dbname=target_connection_string["dbname"],
        user=target_connection_string["user"],
        password=target_connection_string["password"],
        host=target_connection_string["host"],
        port=target_connection_string["port"]
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(insert_sql, tuple(values_for_pg))
        conn.commit()
    
    # Increment migrated_rows count, passing the current status
    database.update_data_migration_job_status(job_id, status=job["status"], migrated_rows=job["migrated_rows"] + 1)

def create_main_jobs_table():
    """Ensures the main migration_jobs.jobs table exists."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "migration_jobs"),
            user=os.getenv("POSTGRES_USER", "migration_jobs"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
        )
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS migration_jobs;
            CREATE TABLE IF NOT EXISTS migration_jobs.jobs (
                job_id UUID PRIMARY KEY,
                status VARCHAR(50) NOT NULL,
                original_sql TEXT,
                converted_sql TEXT,
                job_type VARCHAR(50) NOT NULL,
                error_message TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_jobs_status ON migration_jobs.jobs (status);
            CREATE INDEX IF NOT EXISTS idx_jobs_job_type ON migration_jobs.jobs (job_type);
        """)
        print("Ensured migration_jobs.jobs table exists.")
        cursor.close()
    except psycopg2.Error as e:
        print(f"Error during main jobs table migration: {e}")
    finally:
        if conn:
            conn.close()

def create_extraction_job_tables():
    """Creates tables for different types of extraction jobs."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "migration_jobs"),
            user=os.getenv("POSTGRES_USER", "migration_jobs"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
        )
        conn.autocommit = True
        cursor = conn.cursor()

        object_types = ['table', 'view', 'procedure', 'function', 'index', 'package', 'trigger']

        for obj_type in object_types:
            table_name = f"migration_jobs.{obj_type}_extraction_jobs"
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    job_id UUID PRIMARY KEY,
                    parent_job_id UUID NOT NULL REFERENCES migration_jobs.jobs(job_id),
                    status VARCHAR(50) NOT NULL,
                    object_type VARCHAR(50) NOT NULL,
                    object_name VARCHAR(255) NOT NULL,
                    source_schema VARCHAR(255) NOT NULL,
                    extracted_ddl TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_{obj_type}_extraction_parent_job_id ON {table_name} (parent_job_id);
                CREATE INDEX IF NOT EXISTS idx_{obj_type}_extraction_status ON {table_name} (status);
            """)
            print(f"Ensured table {table_name} exists.")

        cursor.close()
        print("Extraction job tables migration completed successfully.")

    except psycopg2.Error as e:
        print(f"Error during extraction job tables migration: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    create_main_jobs_table()
    migrate_sql_execution_jobs()
    create_extraction_job_tables()
