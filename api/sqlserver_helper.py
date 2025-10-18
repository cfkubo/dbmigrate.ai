
import logging
import pyodbc
from . import models
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)

@contextmanager
def get_sqlserver_connection(user, password, host, port, database):
    """Establishes a connection to the SQL Server database and yields it."""
    connection = None
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={host},{port};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
        )
        connection = pyodbc.connect(conn_str)
        yield connection
    except pyodbc.Error as e:
        raise RuntimeError(f"Error connecting to SQL Server: {e}") from e
    finally:
        if connection:
            connection.close()

def get_sqlserver_schemas(details: models.SQLServerConnectionDetails) -> list[str]:
    """Connects to a SQL Server database and returns a list of schemas."""
    try:
        with get_sqlserver_connection(details.user, details.password, details.host, details.port, details.database) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sys.schemas ORDER BY name")
            schemas = [row[0] for row in cursor]
            logging.info(f"Found {len(schemas)} SQL Server schemas.")
            return schemas
    except pyodbc.Error as e:
        raise RuntimeError(f"Error fetching schemas: {e}") from e

def list_sqlserver_objects(details: models.SQLServerConnectionDetails, schema_name: str, object_type: str) -> list[str]:
    """Lists objects for a given schema and object type in SQL Server."""
    query_map = {
        "TABLE": "SELECT name FROM sys.tables WHERE schema_id = SCHEMA_ID(?) ORDER BY name",
        "VIEW": "SELECT name FROM sys.views WHERE schema_id = SCHEMA_ID(?) ORDER BY name",
        "PROCEDURE": "SELECT name FROM sys.procedures WHERE schema_id = SCHEMA_ID(?) ORDER BY name",
        "FUNCTION": "SELECT name FROM sys.objects WHERE schema_id = SCHEMA_ID(?) AND type IN ('FN', 'IF', 'TF') ORDER BY name",
    }
    
    query = query_map.get(object_type.upper())
    if not query:
        raise ValueError(f"Unsupported object type for SQL Server: {object_type}")

    try:
        with get_sqlserver_connection(details.user, details.password, details.host, details.port, details.database) as connection:
            cursor = connection.cursor()
            cursor.execute(query, schema_name)
            objects = [row[0] for row in cursor]
            return objects
    except pyodbc.Error as e:
        raise RuntimeError(f"Error fetching objects from SQL Server: {e}") from e

def get_sqlserver_ddl(details: models.SQLServerConnectionDetails, schemas: list[str], object_types: list[str], object_names: list[str] | None = None, select_all: bool = False):
    """Extracts DDLs for specified schemas and object types from SQL Server."""
    ddls = {obj_type: {} for obj_type in object_types}
    
    try:
        with get_sqlserver_connection(details.user, details.password, details.host, details.port, details.database) as connection:
            cursor = connection.cursor()
            
            for schema in schemas:
                for obj_type in object_types:
                    objects_to_fetch = []
                    if not object_names or select_all:
                        objects_to_fetch = list_sqlserver_objects(details, schema, obj_type)
                    else:
                        objects_to_fetch = object_names

                    for obj_name in objects_to_fetch:
                        try:
                            # For SQL Server, sp_helptext is a common way to get DDL
                            # This might need adjustments for different object types
                            cursor.execute("sp_helptext ?", f'[{schema}].[{obj_name}]')
                            ddl_rows = cursor.fetchall()
                            if ddl_rows:
                                ddl = "".join([row[0] for row in ddl_rows])
                                key = f"{schema}.{obj_name}"
                                ddls[obj_type][key] = ddl

                        except pyodbc.Error as e:
                            logging.error(f"Error fetching DDL for {obj_type} '{obj_name}' in schema '{schema}': {e}")

        return ddls
    except pyodbc.Error as e:
        raise RuntimeError(f"Error fetching DDL from SQL Server: {e}") from e
