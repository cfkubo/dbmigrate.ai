import psycopg2
import psycopg2.extras
import uuid
import datetime
import json
import logging
import sqlparse
from typing import Optional, List, Dict
from opentelemetry.trace import get_current_span

from api.db_config import (
    valkey_client,
    get_db_connection,
    get_verification_db_connection,
    get_db_connection_by_db_name,
    _convert_uuids_to_strings,
    initialize_db_pool,
    initialize_verification_db_pool,
)

from api.job_repository import (
    get_job_table_names,
    get_data_migration_job,
    get_paginated_jobs_from_table,
    create_job,
    get_job,
    update_job_status,
    get_pending_jobs,
    get_verified_by_worker_jobs,
    create_data_migration_job,
    update_data_migration_job_status,
    log_migration_row_status,

    create_sql_execution_job,
    get_sql_execution_job,
    update_sql_execution_job_status,
    get_all_child_job_statuses,
    get_jobs_by_ids,
)

from api.postgres_utils import (
    execute_sql_from_file,
    create_schema_if_not_exists,
    get_postgres_schemas,
    list_postgres_tables,
    create_postgres_database,
    create_user_if_not_exists,
    get_postgres_table_column_names,
    get_postgres_table_ddl,
    generate_postgres_insert_statements,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

psycopg2.extras.register_uuid()