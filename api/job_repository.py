import psycopg2
import psycopg2.extras
import uuid
import datetime
import json
import logging
import sqlparse
from typing import Optional, List, Dict
from opentelemetry.trace import get_current_span
from psycopg2.sql import SQL, Literal, Identifier

from api.db_config import valkey_client, get_db_connection, _convert_uuids_to_strings

logger = logging.getLogger(__name__)

def get_job_table_names() -> list[str]:
    return ['migration_jobs.jobs', 'migration_jobs.data_migration_jobs', 'migration_jobs.sql_execution_jobs']

def get_data_migration_job(job_id: str) -> Optional[dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM migration_jobs.data_migration_jobs WHERE job_id = %s", (job_id,))
        job = cursor.fetchone()
        cursor.close()
        return job

def get_paginated_jobs_from_table(table_name: str, page: int = 1, size: int = 20, search: Optional[str] = None, status: Optional[str] = None) -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        base_query = f"FROM migration_jobs.{table_name}"
        where_clauses = []
        params = []

        if search:
            # This is a simplification. A real implementation might need to check table columns.
            where_clauses.append("(job_id::text ILIKE %s OR original_sql ILIKE %s OR converted_sql ILIKE %s)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])

        if status and status != "all":
            where_clauses.append("status = %s")
            params.append(status)

        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)

        count_query = "SELECT COUNT(*) " + base_query
        cursor.execute(count_query, tuple(params))
        total_jobs = cursor.fetchone()[0]
        total_pages = (total_jobs + size - 1) // size if size > 0 else 1

        timestamp_column = "created_at"
        select_query = "SELECT * " + base_query + f" ORDER BY {timestamp_column} DESC NULLS LAST, job_id"
        offset = (page - 1) * size
        select_query += " LIMIT %s OFFSET %s"
        params.extend([size, offset])
        
        cursor.execute(select_query, tuple(params))
        jobs = cursor.fetchall()
        cursor.close()

        jobs_list = []
        for job in jobs:
            job_dict = dict(job)
            created = job_dict.get(timestamp_column)
            if isinstance(created, datetime.datetime):
                job_dict[timestamp_column] = created.isoformat()
            jobs_list.append(_convert_uuids_to_strings(job_dict))

    return {"jobs": jobs_list, "total_pages": total_pages}

def create_data_migration_job(
    source_db_type: str,
    source_connection_string: str,
    source_schema_name: str,
    source_table_name: str,
    target_db_type: str,
    target_connection_string: str,
    target_schema_name: str,
    target_table_name: str
) -> str:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        job_id = uuid.uuid4()

        # Get current OpenTelemetry trace ID
        current_span = get_current_span()
        trace_id = format(current_span.context.trace_id, "032x") if current_span.context.trace_id != 0 else "no-trace-id"

        # Store job_id to trace_id mapping in Valkey
        valkey_client.set(f"job:{job_id}:trace_id", trace_id)
        logger.info(f"Stored job_id {job_id} with trace_id {trace_id} in Valkey.")

        cursor.execute(
            """
            INSERT INTO migration_jobs.data_migration_jobs (
                job_id, status, source_db_type, source_connection_string,
                source_schema_name, source_table_name, target_db_type,
                target_connection_string, target_schema_name, target_table_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                job_id, 'pending', source_db_type, source_connection_string,
                source_schema_name, source_table_name, target_db_type,
                target_connection_string, target_schema_name, target_table_name
            )
        )
        conn.commit()
        cursor.close()
        return str(job_id)


def update_data_migration_job_status(
    job_id: str,
    status: str,
    total_rows: Optional[int] = None,
    migrated_rows: Optional[int] = None,
    error_details: Optional[str] = None
):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        update_fields = ["status = %s"]
        update_values = [status]

        if total_rows is not None:
            update_fields.append("total_rows = %s")
            update_values.append(total_rows)
        if migrated_rows is not None:
            update_fields.append("migrated_rows = %s")
            update_values.append(migrated_rows)
        if error_details is not None:
            update_fields.append("error_details = %s")
            update_values.append(error_details)
        
        update_values.append(job_id) # Add job_id for WHERE clause

        query = f"UPDATE migration_jobs.data_migration_jobs SET {', '.join(update_fields)} WHERE job_id = %s"
        cursor.execute(query, tuple(update_values))
        conn.commit()
        cursor.close()

def log_migration_row_status(job_id: str, source_pk_value: str, status: str, error_message: Optional[str] = None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if status == "MIGRATED":
            cursor.execute(
                """
                UPDATE migration_jobs.data_migration_jobs
                SET migrated_rows = COALESCE(migrated_rows, 0) + 1
                WHERE job_id = %s
                """,
                (job_id,)
            )
        elif status == "FAILED":
            # Append error message to error_details (JSONB array)
            cursor.execute(
                """
                UPDATE migration_jobs.data_migration_jobs
                SET failed_rows = COALESCE(failed_rows, 0) + 1,
                    error_details = COALESCE(error_details, '[]'::jsonb) || jsonb_build_object('pk_value', %s, 'error', %s)
                WHERE job_id = %s
                """,
                (source_pk_value, error_message, job_id)
            )
        conn.commit()
        cursor.close()


def create_job(
    job_type: str,
    original_sql: Optional[str] = None,
    parent_job_id: Optional[str] = None,
    source_db_type: Optional[str] = None,
    target_db_type: Optional[str] = None,
    source_connection_details: Optional[dict] = None,
    target_connection_details: Optional[dict] = None,
    source_schema: Optional[str] = None,
    target_schema: Optional[str] = None,
    object_type: Optional[str] = None,
    object_name: Optional[str] = None,
    data_migration_enabled: Optional[bool] = False
) -> str:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        job_id = uuid.uuid4()

        current_span = get_current_span()
        trace_id = format(current_span.context.trace_id, "032x") if current_span.context.trace_id != 0 else "no-trace-id"
        valkey_client.set(f"job:{job_id}:trace_id", trace_id)
        logger.info(f"Stored job_id {job_id} with trace_id {trace_id} in Valkey.")

        # Construct the INSERT statement dynamically based on provided arguments
        columns = ["job_id", "status", "job_type", "extraction_status", "conversion_status", "execution_status", "data_migration_status"]
        values = [job_id, 'pending', job_type, 'pending', 'pending', 'pending', 'pending']
        placeholders = ["%s", "%s", "%s", "%s", "%s", "%s", "%s"]

        if original_sql is not None:
            columns.append("original_sql")
            values.append(original_sql)
            placeholders.append("%s")
        else:
            columns.append("original_sql")
            values.append("") # Default to empty string if not provided
            placeholders.append("%s")

        if parent_job_id is not None:
            columns.append("parent_job_id")
            values.append(parent_job_id)
            placeholders.append("%s")
        if source_db_type is not None:
            columns.append("source_db_type")
            values.append(source_db_type)
            placeholders.append("%s")
        if target_db_type is not None:
            columns.append("target_db_type")
            values.append(target_db_type)
            placeholders.append("%s")
        if source_connection_details is not None:
            columns.append("source_connection_details")
            values.append(json.dumps(source_connection_details))
            placeholders.append("%s")
        if target_connection_details is not None:
            columns.append("target_connection_details")
            values.append(json.dumps(target_connection_details))
            placeholders.append("%s")
        if source_schema is not None:
            columns.append("source_schema")
            values.append(source_schema)
            placeholders.append("%s")
        if target_schema is not None:
            columns.append("target_schema")
            values.append(target_schema)
            placeholders.append("%s")
        if object_type is not None:
            columns.append("object_type")
            values.append(object_type)
            placeholders.append("%s")
        if object_name is not None:
            columns.append("object_name")
            values.append(object_name)
            placeholders.append("%s")
        if data_migration_enabled is not None:
            columns.append("data_migration_enabled")
            values.append(data_migration_enabled)
            placeholders.append("%s")

        insert_query = f"INSERT INTO migration_jobs.jobs ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(insert_query, tuple(values))
        conn.commit()
        cursor.close()
        return str(job_id)

def get_job(job_id: str) -> Optional[dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM migration_jobs.jobs WHERE job_id = %s", (job_id,))
        job = cursor.fetchone()
        cursor.close()
        return job

def get_jobs_by_ids(job_ids: List[str]) -> List[Dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Using psycopg2.extras.execute_values for efficient IN clause with multiple values
        # Note: execute_values is typically for INSERT/UPDATE. For SELECT with IN,
        # it's more common to use a single %s with a tuple of values.
        # Let's adjust this to the more standard approach for SELECT IN.
        query = "SELECT * FROM migration_jobs.jobs WHERE job_id = ANY(%s::uuid[])"
        cursor.execute(query, (job_ids,))
        jobs = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        job_dicts = []
        for job_tuple in jobs:
            job_dicts.append(dict(zip(column_names, job_tuple)))
        cursor.close()
        return job_dicts

def update_job_status(job_id, status, original_sql=None, converted_sql=None, error_message=None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        update_fields = ["status = %s"]
        update_values = [status]

        if status == 'verified':
            if converted_sql is not None:
                update_fields.append("converted_sql = %s")
                update_values.append(converted_sql)
        else:
            if original_sql is not None:
                update_fields.append("original_sql = %s")
                update_values.append(original_sql)
            if converted_sql is not None:
                update_fields.append("converted_sql = %s")
                update_values.append(converted_sql)

        if error_message is not None:
            update_fields.append("error_message = %s")
            update_values.append(error_message)
        
        update_values.append(job_id) # Add job_id for WHERE clause

        query = f"UPDATE migration_jobs.jobs SET {', '.join(update_fields)} WHERE job_id = %s"
        cursor.execute(query, tuple(update_values))
        conn.commit()
        cursor.close()

def update_child_job_stage_status(job_id: str, stage_name: str, status: str, error_message: Optional[str] = None, converted_ddl: Optional[str] = None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        update_fields = [f"{stage_name}_status = %s"]
        update_values = [status]

        if error_message is not None:
            update_fields.append("error_message = %s")
            update_values.append(error_message)
        if converted_ddl is not None:
            update_fields.append("converted_sql = %s") # Assuming converted_sql stores the DDL
            update_values.append(converted_ddl)
        
        update_values.append(job_id) # Add job_id for WHERE clause

        query = f"UPDATE migration_jobs.jobs SET {', '.join(update_fields)} WHERE job_id = %s"
        cursor.execute(query, tuple(update_values))
        conn.commit()
        cursor.close()

def get_all_child_job_statuses(parent_job_id: str) -> List[Dict]:
    all_child_jobs_status = []
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = """
            SELECT
                mj.job_id,
                mj.job_type,
                mj.object_type,
                mj.object_name,
                mj.status AS overall_status,
                mj.error_message AS overall_error_message,
                mj.original_sql,
                mj.converted_sql,
                mj.extraction_status,
                mj.conversion_status,
                mj.execution_status AS job_execution_status,
                mj.data_migration_status AS job_data_migration_status,
                sej.status AS sql_execution_status,
                sej.error_message AS sql_execution_error_message,
                dmj.status AS data_migration_status,
                dmj.error_details AS data_migration_error_details
            FROM
                migration_jobs.jobs mj
            LEFT JOIN
                migration_jobs.sql_execution_jobs sej ON mj.job_id = sej.job_id
            LEFT JOIN
                migration_jobs.data_migration_jobs dmj ON mj.job_id = dmj.job_id
            WHERE
                mj.parent_job_id = %s
        """
        cursor.execute(query, (str(parent_job_id),))
        jobs_data = cursor.fetchall()

        for job in jobs_data:
            job_dict = dict(job)
            
            # Aggregate statuses, prioritizing specific job table statuses if available
            # For execution, if sql_execution_status is available, use it, otherwise use job_execution_status
            execution_status = job_dict["sql_execution_status"] if job_dict["sql_execution_status"] else job_dict["job_execution_status"]
            execution_error = job_dict["sql_execution_error_message"] if job_dict["sql_execution_error_message"] else None

            # For data migration, if data_migration_status is available, use it, otherwise use job_data_migration_status
            data_migration_status = job_dict["data_migration_status"] if job_dict["data_migration_status"] else job_dict["job_data_migration_status"]
            data_migration_error = job_dict["data_migration_error_details"] if job_dict["data_migration_error_details"] else None

            # Consolidate error messages
            error_message = job_dict["overall_error_message"]
            if data_migration_error:
                if error_message:
                    error_message += f"; Data Migration Error: {json.dumps(data_migration_error)}"
                else:
                    error_message = f"Data Migration Error: {json.dumps(data_migration_error)}"

            all_child_jobs_status.append({
                "job_id": str(job_dict["job_id"]),
                "object_type": job_dict.get("object_type", "unknown"),
                "object_name": job_dict.get("object_name", "unknown"),
                "status": job_dict["overall_status"], # Overall status of the child job
                "error_message": error_message,
                "original_sql": job_dict["original_sql"] or "",
                "converted_ddl": job_dict["converted_sql"],
                "extraction_status": job_dict["extraction_status"],
                "conversion_status": job_dict["conversion_status"],
                "execution_status": execution_status,
                "execution_error": execution_error,
                "data_migration_status": data_migration_status,
                "data_migration_error": data_migration_error,
            })

        cursor.close()
    return all_child_jobs_status

# --- SQL Execution Jobs --- #

def create_sql_execution_job(filename: str, sanitized_sql: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        job_id = uuid.uuid4()
        logger.info(f"Attempting to create SQL execution job with ID: {job_id}")

        # Get current OpenTelemetry trace ID
        current_span = get_current_span()
        trace_id = format(current_span.context.trace_id, "032x") if current_span.context.trace_id != 0 else "no-trace-id"

        # Store job_id to trace_id mapping in Valkey
        valkey_client.set(f"job:{job_id}:trace_id", trace_id)
        logger.info(f"Stored job_id {job_id} with trace_id {trace_id} in Valkey.")

        cursor.execute(
            "INSERT INTO migration_jobs.sql_execution_jobs (job_id, status, filename, sanitized_sql, statement_results) VALUES (%s, %s, %s, %s, %s)",
            (job_id, 'pending', filename, sanitized_sql, '[]') # Initialize with empty JSON array
        )
        conn.commit()
        logger.info(f"SQL execution job {job_id} created and committed.")
        logger.debug(f"Created SQL execution job with ID: {job_id}")
        cursor.close()
        return str(job_id)

def get_sql_execution_job(job_id: str) -> Optional[dict]:
    print(f"[DEBUG] get_sql_execution_job called for job_id: {job_id}")
    logger.debug(f"Searching for SQL execution job with ID: {job_id}")
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        logger.info(f"Attempting to retrieve SQL execution job with ID: {job_id}")
        cursor.execute("SELECT * FROM migration_jobs.sql_execution_jobs WHERE job_id = %s", (job_id,))
        job = cursor.fetchone()
        if job:
            logger.info(f"SQL execution job {job_id} found. Raw job data: {job}")
        else:
            logger.warning(f"SQL execution job {job_id} not found.")
        cursor.close()
        return job

def update_sql_execution_job_status(job_id: str, status: str, error_message: Optional[str] = None, statement_results: Optional[list] = None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        processed_at = datetime.datetime.now(datetime.timezone.utc)
        if statement_results is not None:
            cursor.execute(
                "UPDATE migration_jobs.sql_execution_jobs SET status = %s, error_message = %s, processed_at = %s, statement_results = %s WHERE job_id = %s",
                (status, error_message, processed_at, json.dumps(statement_results), job_id)
            )
        else:
            cursor.execute(
                "UPDATE migration_jobs.sql_execution_jobs SET status = %s, error_message = %s, processed_at = %s WHERE job_id = %s",
                (status, error_message, processed_at, job_id)
            )
        conn.commit()
        cursor.close()

def get_pending_jobs():
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM migration_jobs.jobs WHERE status = 'pending'")
        jobs = cursor.fetchall()
        cursor.close()
        return jobs

def get_verified_by_worker_jobs():
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM migration_jobs.jobs WHERE status = 'verified_by_worker'")
        jobs = cursor.fetchall()
        cursor.close()
        return jobs