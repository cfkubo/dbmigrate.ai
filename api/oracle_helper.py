import logging
import oracledb
from . import models
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)

@contextmanager
def get_oracle_connection(user, password, host, port, service_name=None, sid=None):
    """Establishes a connection to the Oracle database and yields it.
    Handles both service_name and sid for DSN creation.
    """
    if sid:
        dsn = oracledb.makedsn(host, port, sid=sid)
    elif service_name:
        dsn = oracledb.makedsn(host, port, service_name=service_name)
    else:
        raise RuntimeError("Either a Service Name or SID must be provided.")
    
    connection = None
    try:
        connection = oracledb.connect(user=user, password=password, dsn=dsn)
        yield connection
    except oracledb.Error as e:
        raise RuntimeError(f"Error connecting to Oracle: {e}") from e
    finally:
        if connection:
            connection.close()

def get_oracle_schemas(details: models.OracleConnectionDetails) -> list[str]:
    """Connects to an Oracle database and returns a list of schemas.

    Args:
        details: The Oracle connection details.

    Returns:
        A list of schema names.
    """
    try:
        with get_oracle_connection(details.user, details.password, details.host, details.port, details.service_name, details.sid) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT username FROM dba_users ORDER BY username")
            schemas = [row[0] for row in cursor]
            logging.info(f"Found {len(schemas)} Oracle schemas.")
            return schemas
    except oracledb.Error as e:
        raise RuntimeError(f"Error fetching schemas: {e}") from e

def list_oracle_objects(details: models.OracleConnectionDetails, schema_name: str, object_type: str) -> list[str]:
    """Connects to an Oracle database and lists objects for a given schema and object type.

    Args:
        details: The Oracle connection details.
        schema: The schema to list objects from.
        object_type: The type of object to list.

    Returns:
        A list of object names.
    """
    try:
        with get_oracle_connection(details.user, details.password, details.host, details.port, details.service_name, details.sid) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT object_name
                FROM dba_objects
                WHERE owner = :schema_name
                AND object_type = :obj_type
                ORDER BY object_name
                """,
                schema_name=schema_name.upper(),
                obj_type=object_type.upper()
            )
            objects = [row[0] for row in cursor]
            return objects
    except oracledb.Error as e:
        raise RuntimeError(f"Error fetching objects: {e}") from e

def get_oracle_ddl(details: models.OracleConnectionDetails, schemas: list[str], object_types: list[str], object_names: list[str] | None = None, select_all: bool = False):
    """Connects to an Oracle database and extracts DDLs for specified schemas and object types.

    Args:
        details: The Oracle connection details.
        schemas: A list of schemas to extract DDLs from.
        object_types: A list of object types to extract.
        object_names: An optional list of object names to extract.

    Returns:
        A dictionary containing the DDLs.
    """
    logging.info(f"Starting DDL extraction for schemas: {schemas}, object types: {object_types}")

    ddls = {obj_type: {} for obj_type in ['TABLE', 'VIEW', 'PROCEDURE', 'FUNCTION', 'INDEX', 'PACKAGE', 'TRIGGER']}
    ddls["db_name"] = ""
    try:
        with get_oracle_connection(details.user, details.password, details.host, details.port, details.service_name, details.sid) as connection:
            logging.info(f"Successfully connected to Oracle database")
            cursor = connection.cursor()
            
            # Configure DBMS_METADATA for cleaner DDL output
            cursor.execute("""
                BEGIN
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'STORAGE', FALSE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SEGMENT_ATTRIBUTES', FALSE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SQLTERMINATOR', TRUE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'PRETTY', TRUE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'CONSTRAINTS_AS_ALTER', FALSE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'REF_CONSTRAINTS', TRUE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'EMIT_SCHEMA', FALSE);
                END;
            """)

            if not ddls["db_name"]:
                cursor.execute("SELECT ORA_DATABASE_NAME FROM DUAL")
                db_name = cursor.fetchone()[0]
                ddls["db_name"] = db_name
                logging.info(f"Database name: {db_name}")

            for schema in schemas:
                logging.info(f"Processing schema: {schema}")
                for obj_type in object_types:
                    logging.info(f"Processing object type: {obj_type} for schema: {schema}")
                    
                    objects_to_fetch = []
                    if not object_names or select_all:
                        cursor.execute("""
                            SELECT object_name
                            FROM dba_objects
                            WHERE owner = :schema_name
                            AND object_type = :obj_type
                            ORDER BY object_name
                            """,
                            schema_name=schema.upper(),
                            obj_type=obj_type.upper()
                        )
                        objects_to_fetch = [row[0] for row in cursor]
                    else:
                        objects_to_fetch = object_names
                    
                    logging.info(f"Found {len(objects_to_fetch)} objects to fetch for {obj_type}.")

                    for obj_name in objects_to_fetch:
                        try:
                            cursor.execute(
                                "SELECT DBMS_METADATA.GET_DDL(:obj_type, :obj_name, :schema_name) FROM DUAL",
                                obj_type=obj_type.upper(),
                                obj_name=obj_name,
                                schema_name=schema.upper()
                            )
                            ddl_clob = cursor.fetchone()
                            if ddl_clob and ddl_clob[0]:
                                ddl = ddl_clob[0].read()
                                key = f"{schema}.{obj_name}"
                                ddls[obj_type][key] = ddl
                            else:
                                logging.warning(f"No DDL found for {obj_type} '{obj_name}'.")
                        except oracledb.Error as e:
                            error_obj, = e.args
                            logging.error(f"Error fetching DDL for {obj_type} '{obj_name}': {error_obj.message}")
        return ddls
    except oracledb.Error as e:
        logging.error(f"Error fetching DDL: {e}")
        raise RuntimeError(f"Error fetching DDL: {e}") from e

def get_oracle_table_ddl(details: models.OracleConnectionDetails, schema_name: str, table_name: str) -> str | None:
    """Retrieves the DDL for a specific Oracle table.

    Args:
        details: The Oracle connection details.
        schema_name: The name of the schema the table belongs to.
        table_name: The name of the table.

    Returns:
        A string containing the DDL for the table, or None if not found.
    """
    try:
        clean_table_name = table_name.split('.')[-1]
        with get_oracle_connection(details.user, details.password, details.host, details.port, details.service_name, details.sid) as connection:
            cursor = connection.cursor()
            # Configure DBMS_METADATA for cleaner DDL output
            cursor.execute("""
                BEGIN
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'STORAGE', FALSE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SEGMENT_ATTRIBUTES', FALSE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SQLTERMINATOR', TRUE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'PRETTY', TRUE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'CONSTRAINTS_AS_ALTER', FALSE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'REF_CONSTRAINTS', TRUE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'EMIT_SCHEMA', FALSE);
                END;
            """)
            cursor.execute(
                "SELECT DBMS_METADATA.GET_DDL('TABLE', :obj_name, :schema_name) FROM DUAL",
                obj_name=clean_table_name.upper(),
                schema_name=schema_name.upper()
            )
            ddl_clob = cursor.fetchone()
            if ddl_clob and ddl_clob[0]:
                return ddl_clob[0].read()
            return None
    except oracledb.Error as e:
        logging.error(f"Error fetching Oracle DDL for {schema_name}.{table_name}: {e}")
        return None

def fetch_oracle_table_data_batched(
    details: models.OracleConnectionDetails,
    schema_name: str,
    table_name: str,
    batch_size: int = 1000
) -> tuple[list[str], list[list]]:
    """
    Fetches data from a specified Oracle table in batches.

    Args:
        details: The Oracle connection details.
        schema_name: The name of the schema the table belongs to.
        table_name: The name of the table.
        batch_size: The number of rows to fetch in each batch.

    Returns:
        A tuple containing:
        - A list of column names.
        - A list of lists, where each inner list represents a batch of rows.
    """
    all_rows = []
    column_names = []
    try:
        with get_oracle_connection(details.user, details.password, details.host, details.port, details.service_name, details.sid) as connection:
            cursor = connection.cursor()
            query = f"SELECT * FROM {schema_name.upper()}.{table_name.upper()}"
            cursor.execute(query)

            # Get column names
            column_names = [col[0] for col in cursor.description]

            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break
                all_rows.extend(rows)
        logging.info(f"Successfully fetched {len(all_rows)} rows from Oracle table {schema_name}.{table_name}.")
        return column_names, all_rows
    except oracledb.Error as e:
        logging.error(f"Error fetching data from Oracle table {schema_name}.{table_name}: {e}")
        raise RuntimeError(f"Error fetching data from Oracle table: {e}") from e

def test_oracle_ddl_extraction(details: models.OracleConnectionDetails):
    """
    Tests the connection and DDL extraction from an Oracle database.

    Args:
        details: The Oracle connection details.

    Returns:
        A success message if the extraction is successful, otherwise raises a RuntimeError.
    """
    try:
        with get_oracle_connection(details.user, details.password, details.host, details.port, details.service_name, details.sid) as connection:
            cursor = connection.cursor()

            # Configure DBMS_METADATA for cleaner DDL output
            cursor.execute("""
                BEGIN
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'STORAGE', FALSE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SEGMENT_ATTRIBUTES', FALSE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SQLTERMINATOR', TRUE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'PRETTY', TRUE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'CONSTRAINTS_AS_ALTER', FALSE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'REF_CONSTRAINTS', TRUE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'EMIT_SCHEMA', FALSE);
                END;
            """)

            # Try to fetch the DDL for a single, common object to test permissions
            cursor.execute("""
                SELECT object_name, owner
                FROM dba_objects
                WHERE object_type = 'TABLE' AND ROWNUM = 1
            """)
            result = cursor.fetchone()
            if not result:
                raise RuntimeError("DDL extraction test failed. No tables found in accessible schemas.")

            object_name, owner = result
            cursor.execute(
                "SELECT DBMS_METADATA.GET_DDL('TABLE', :object_name, :owner) FROM DUAL",
                object_name=object_name,
                owner=owner
            )
            ddl_clob = cursor.fetchone()[0]
            
            if ddl_clob and ddl_clob.read():
                return "DDL extraction test successful. Permissions appear to be correct."
            else:
                raise RuntimeError("DDL extraction test failed. Could not fetch any DDL. Please ensure the user has the necessary permissions (e.g., SELECT ANY DICTIONARY or SELECT_CATALOG_ROLE) and that there are objects in the accessible schemas.")
    except oracledb.Error as e:
        raise RuntimeError(f"Error connecting to Oracle or fetching DDL: {e}") from e

def _get_oracle_ddl_for_type(details: models.OracleConnectionDetails, schema_name: str, object_name: str, object_type: str) -> str | None:
    """
    Retrieves the DDL for a specific Oracle object.

    Args:
        details: The Oracle connection details.
        schema_name: The name of the schema the object belongs to.
        object_name: The name of the object.
        object_type: The type of the object (e.g., 'TABLE', 'VIEW').

    Returns:
        A string containing the DDL for the object, or None if not found.
    """
    try:
        clean_object_name = object_name.split('.')[-1]
        with get_oracle_connection(details.user, details.password, details.host, details.port, details.service_name, details.sid) as connection:
            cursor = connection.cursor()
            # Configure DBMS_METADATA for cleaner DDL output
            cursor.execute("""
                BEGIN
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'STORAGE', FALSE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SEGMENT_ATTRIBUTES', FALSE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SQLTERMINATOR', TRUE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'PRETTY', TRUE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'CONSTRAINTS_AS_ALTER', FALSE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'REF_CONSTRAINTS', TRUE);
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'EMIT_SCHEMA', FALSE);
                END;
            """)
            cursor.execute(
                "SELECT DBMS_METADATA.GET_DDL(:obj_type, :obj_name, :schema_name) FROM DUAL",
                obj_type=object_type.upper(),
                obj_name=clean_object_name.upper(),
                schema_name=schema_name.upper()
            )
            ddl_clob = cursor.fetchone()
            if ddl_clob and ddl_clob[0]:
                return ddl_clob[0].read()
            return None
    except oracledb.Error as e:
        logging.error(f"Error fetching Oracle DDL for {object_type} {schema_name}.{object_name}: {e}")
        return None

def get_oracle_view_ddl(details: models.OracleConnectionDetails, schema_name: str, view_name: str) -> str | None:
    return _get_oracle_ddl_for_type(details, schema_name, view_name, 'VIEW')

def get_oracle_procedure_ddl(details: models.OracleConnectionDetails, schema_name: str, procedure_name: str) -> str | None:
    return _get_oracle_ddl_for_type(details, schema_name, procedure_name, 'PROCEDURE')

def get_oracle_function_ddl(details: models.OracleConnectionDetails, schema_name: str, function_name: str) -> str | None:
    return _get_oracle_ddl_for_type(details, schema_name, function_name, 'FUNCTION')

def get_oracle_index_ddl(details: models.OracleConnectionDetails, schema_name: str, index_name: str) -> str | None:
    return _get_oracle_ddl_for_type(details, schema_name, index_name, 'INDEX')

def get_oracle_package_ddl(details: models.OracleConnectionDetails, schema_name: str, package_name: str) -> str | None:
    return _get_oracle_ddl_for_type(details, schema_name, package_name, 'PACKAGE')

def get_oracle_trigger_ddl(details: models.OracleConnectionDetails, schema_name: str, trigger_name: str) -> str | None:
    return _get_oracle_ddl_for_type(details, schema_name, trigger_name, 'TRIGGER')