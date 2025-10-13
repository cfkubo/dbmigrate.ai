import psycopg2
import psycopg2.extras
import uuid
import datetime
import logging
import sqlparse
from typing import Optional, List

from api.db_config import get_db_connection, get_db_connection_by_db_name

logger = logging.getLogger(__name__)

def execute_sql_from_file(conn, file_path):
    """Executes SQL commands from a file, splitting them into individual statements."""
    try:
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        # Use sqlparse to split the content into individual statements
        statements = sqlparse.split(sql_content)
        
        cursor = conn.cursor()
        for statement in statements:
            # Only execute non-empty statements
            if statement.strip():
                try:
                    cursor.execute(statement)
                    logger.info(f"Successfully executed statement from {file_path}: {statement.strip()[:100]}...")
                except Exception as e:
                    logger.error(f"Error executing statement from {file_path}: {statement.strip()}\n{e}", exc_info=True)
                    conn.rollback() # Rollback on error
                    return # Stop execution on the first error
        conn.commit()
        cursor.close()
        logger.info(f"All SQL statements from {file_path} executed successfully.")
    except Exception as e:
        logger.error(f"Failed to read or process SQL file {file_path}: {e}", exc_info=True)
        conn.rollback()

def create_schema_if_not_exists(schema_name: str, conn=None):
    """Ensures a schema exists, using an optional connection."""
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
            conn.commit()
            cursor.close()
            logger.info(f"Schema '{schema_name}' ensured to exist using provided connection.")
        except Exception as e:
            logger.error(f"Error creating schema '{schema_name}' with provided connection: {e}", exc_info=True)
    else:
        try:
            with get_db_connection() as default_conn:
                cursor = default_conn.cursor()
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
                default_conn.commit()
                cursor.close()
            logger.info(f"Schema '{schema_name}' ensured to exist using default connection.")
        except Exception as e:
            logger.error(f"Error creating schema '{schema_name}' with default connection: {e}", exc_info=True)

def get_postgres_schemas(dbname: Optional[str] = None) -> list[str]:
    """
    Connects to a PostgreSQL database and returns a list of user-defined schemas.
    If dbname is not provided, it uses the default connection.
    """
    
    connection_context = get_db_connection_by_db_name(dbname) if dbname else get_db_connection()

    with connection_context as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT LIKE 'pg_%' AND schema_name != 'information_schema'
            ORDER BY schema_name;
        """)
        schemas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return schemas


def list_postgres_tables(schema_name: str, dbname: Optional[str] = None) -> list[str]:
    """
    Connects to a PostgreSQL database and returns a list of tables for a given schema.
    If dbname is provided, it connects to that specific database.
    """
    
    connection_context = get_db_connection_by_db_name(dbname) if dbname else get_db_connection()
    
    with connection_context as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """, (schema_name,))
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables



def create_postgres_database(host, port, user, password, dbname_to_create):
    """
    Connects to a PostgreSQL server (using the 'postgres' database) and creates a new database.
    """
    print(f"[DEBUG] Attempting to connect to create DB with: user={user}, password={password}, host={host}, port={port}")
    conn = None


    try:
        # Connect to the default 'postgres' database to create a new one
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname="postgres"  # Connect to default database
        )
        conn.autocommit = True  # Autocommit for CREATE DATABASE
        cursor = conn.cursor()

        # Check if the database already exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{dbname_to_create}'")
        if cursor.fetchone():
            logger.info(f"Database '{dbname_to_create}' already exists. Skipping creation.")
            return True

        cursor.execute(f"CREATE DATABASE {dbname_to_create}")
        logger.info(f"Database '{dbname_to_create}' created successfully.")
        cursor.close()
        return True
    except psycopg2.Error as e:
        logger.error(f"Error creating database '{dbname_to_create}': {e}", exc_info=True)
        return False
    finally:
        if conn:
            conn.close()

def create_user_if_not_exists(host, port, admin_user, admin_password, user_to_create, password_for_new_user):
    """
    Connects to a PostgreSQL server as an admin and creates a new user if it doesn't exist.
    """
    print(f"[DEBUG] Attempting to connect to create USER with: user={admin_user}, password={admin_password}, host={host}, port={port}")
    conn = None
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=admin_user,
            password=admin_password,
            dbname="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if the user already exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = %s", (user_to_create,))
        if cursor.fetchone():
            logger.info(f"User '{user_to_create}' already exists. Skipping creation.")
            return True

        # Create the user with SUPERUSER privilege
        cursor.execute(f"CREATE USER {user_to_create} WITH PASSWORD '{password_for_new_user}' SUPERUSER")
        logger.info(f"User '{user_to_create}' created successfully with SUPERUSER privilege.")
        cursor.close()
        return True
    except psycopg2.Error as e:
        logger.error(f"Error creating user '{user_to_create}': {e}", exc_info=True)
        return False
    finally:
        if conn:
            conn.close()


def get_postgres_table_column_names(schema_name: str, table_name: str, dbname: Optional[str] = None) -> List[str]:
    """
    Retrieves the actual column names (preserving their case) for a given PostgreSQL table.
    """
    connection_context = get_db_connection_by_db_name(dbname) if dbname else get_db_connection()

    with connection_context as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """, (schema_name, table_name))

        column_names = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return column_names

def get_postgres_table_ddl(schema_name: str, table_name: str, dbname: Optional[str] = None) -> Optional[str]:
    """
    Constructs the DDL for a specific PostgreSQL table.
    """
    connection_context = get_db_connection_by_db_name(dbname) if dbname else get_db_connection()

    with connection_context as conn:
        cursor = conn.cursor()
        
        # Get column definitions
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """, (schema_name, table_name))
        
        columns = cursor.fetchall()
        if not columns:
            return None

        ddl = f'CREATE TABLE {schema_name}.{table_name} (\n'
        
        column_defs = []
        for col in columns:
            col_name, data_type, char_max_len, is_nullable, col_default = col
            col_def = f'    "{col_name}" {data_type}'
            if char_max_len:
                col_def += f'({char_max_len})'
            if is_nullable == 'NO':
                col_def += ' NOT NULL'
            if col_default:
                col_def += f' DEFAULT {col_default}'
            column_defs.append(col_def)
        
        ddl += ',\n'.join(column_defs)
        
        # Get constraints
        cursor.execute("""
            SELECT conname, pg_get_constraintdef(oid)
            FROM pg_constraint
            WHERE conrelid = (
                SELECT oid FROM pg_class WHERE relname = %s AND relnamespace = (
                    SELECT oid FROM pg_namespace WHERE nspname = %s
                )
            );
        """, (table_name, schema_name))
        
        constraints = cursor.fetchall()
        if constraints:
            ddl += ',\n'
            constraint_defs = [f'    CONSTRAINT "{con[0]}" {con[1]}' for con in constraints]
            ddl += ',\n'.join(constraint_defs)

        ddl += '\n);'
        
        cursor.close()
        return ddl

def generate_postgres_insert_statements(
    oracle_column_names: list[str],
    oracle_rows: list[tuple],
    postgres_ddl: str,
    target_schema: str,
    target_table: str
) -> list[tuple[str, tuple]]:
    """
    Generates PostgreSQL INSERT statements from Oracle data.

    Args:
        oracle_column_names: List of column names from the Oracle source table.
        oracle_rows: List of tuples, where each tuple is a row of data from Oracle.
        postgres_ddl: The DDL of the target PostgreSQL table.
        target_schema: The target PostgreSQL schema name.
        target_table: The target PostgreSQL table name.

    Returns:
        A list of tuples, where each tuple contains:
        - The INSERT statement string with placeholders.
        - A tuple of values to be inserted.
    """
    insert_statements = []

    # Parse PostgreSQL DDL to get target column names and types
    # This is a simplified parsing. A more robust solution might use a proper SQL parser.
    postgres_columns = []
    for line in postgres_ddl.splitlines():
        if '    "' in line and '"' in line:
            try:
                col_name_start = line.find('"') + 1
                col_name_end = line.find('"', col_name_start)
                column_name = line[col_name_start:col_name_end]
                postgres_columns.append(column_name)
            except Exception as e:
                logger.warning(f"Could not parse column from DDL line: {line}. Error: {e}")

    if not postgres_columns:
        raise ValueError("Could not extract column names from PostgreSQL DDL.")

    # Ensure column names are case-insensitive for mapping
    oracle_col_map = {name.lower(): i for i, name in enumerate(oracle_column_names)}
    postgres_col_map = {name.lower(): name for name in postgres_columns}

    # Determine the columns to insert and their order
    # We assume a 1:1 mapping of column names (case-insensitive) for now.
    # More complex scenarios (e.g., different column names, transformations) would require a mapping configuration.
    insert_cols = []
    value_placeholders = []
    oracle_indices_for_insert = []

    for pg_col_lower, pg_col_original in postgres_col_map.items():
        if pg_col_lower in oracle_col_map:
            insert_cols.append(f'"{pg_col_original}"')
            value_placeholders.append('%s')
            oracle_indices_for_insert.append(oracle_col_map[pg_col_lower])
        else:
            logger.warning(f"PostgreSQL column {pg_col_original} not found in Oracle source. Skipping.")

    if not insert_cols:
        raise ValueError("No matching columns found between Oracle and PostgreSQL for INSERT statements.")

    insert_sql_template = f"INSERT INTO \"{target_schema}\".\"{target_table}\" ({', '.join(insert_cols)}) VALUES ({', '.join(value_placeholders)})"

    for row in oracle_rows:
        values_for_insert = []
        for idx in oracle_indices_for_insert:
            value = row[idx]
            # Basic type handling: convert UUIDs to string, datetime to ISO format
            if isinstance(value, uuid.UUID):
                values_for_insert.append(str(value))
            elif isinstance(value, datetime.datetime):
                values_for_insert.append(value.isoformat())
            else:
                values_for_insert.append(value)
        insert_statements.append((insert_sql_template, tuple(values_for_insert)))

    return insert_statements