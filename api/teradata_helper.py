
import logging
import teradatasql
from . import models
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)

@contextmanager
def get_teradata_connection(user, password, host):
    """Establishes a connection to the Teradata database and yields it."""
    connection = None
    try:
        connection = teradatasql.connect(host=host, user=user, password=password)
        yield connection
    except teradatasql.Error as e:
        raise RuntimeError(f"Error connecting to Teradata: {e}") from e
    finally:
        if connection:
            connection.close()

def get_teradata_schemas(details: models.TeradataConnectionDetails) -> list[str]:
    """Connects to a Teradata database and returns a list of databases (schemas)."""
    try:
        with get_teradata_connection(details.user, details.password, details.host) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT DatabaseName FROM DBC.DatabasesV ORDER BY DatabaseName;")
            schemas = [row[0] for row in cursor]
            logging.info(f"Found {len(schemas)} Teradata databases.")
            return schemas
    except teradatasql.Error as e:
        raise RuntimeError(f"Error fetching databases: {e}") from e

def list_teradata_objects(details: models.TeradataConnectionDetails, schema_name: str, object_type: str) -> list[str]:
    """Lists objects for a given schema and object type in Teradata."""
    query_map = {
        "TABLE": "SELECT TableName FROM DBC.TablesV WHERE DatabaseName = ? AND TableKind = 'T' ORDER BY TableName",
        "VIEW": "SELECT TableName FROM DBC.TablesV WHERE DatabaseName = ? AND TableKind = 'V' ORDER BY TableName",
        "MACRO": "SELECT TableName FROM DBC.TablesV WHERE DatabaseName = ? AND TableKind = 'M' ORDER BY TableName",
        # Add other object types as needed
    }
    
    query = query_map.get(object_type.upper())
    if not query:
        raise ValueError(f"Unsupported object type for Teradata: {object_type}")

    try:
        with get_teradata_connection(details.user, details.password, details.host) as connection:
            cursor = connection.cursor()
            cursor.execute(query, (schema_name,))
            objects = [row[0] for row in cursor]
            return objects
    except teradatasql.Error as e:
        raise RuntimeError(f"Error fetching objects from Teradata: {e}") from e

def get_teradata_ddl(details: models.TeradataConnectionDetails, schemas: list[str], object_types: list[str], object_names: list[str] | None = None, select_all: bool = False):
    """Extracts DDLs for specified schemas and object types from Teradata."""
    ddls = {obj_type: {} for obj_type in object_types}
    
    try:
        with get_teradata_connection(details.user, details.password, details.host) as connection:
            cursor = connection.cursor()
            
            for schema in schemas:
                for obj_type in object_types:
                    objects_to_fetch = []
                    if not object_names or select_all:
                        objects_to_fetch = list_teradata_objects(details, schema, obj_type)
                    else:
                        objects_to_fetch = object_names

                    for obj_name in objects_to_fetch:
                        try:
                            cursor.execute(f"SHOW {obj_type.upper()} \"{schema}\".\"{obj_name}\";")
                            ddl_rows = cursor.fetchall()
                            if ddl_rows:
                                ddl = ddl_rows[0][0]
                                key = f"{schema}.{obj_name}"
                                ddls[obj_type][key] = ddl

                        except teradatasql.Error as e:
                            logging.error(f"Error fetching DDL for {obj_type} '{obj_name}' in schema '{schema}': {e}")

        return ddls
    except teradatasql.Error as e:
        raise RuntimeError(f"Error fetching DDL from Teradata: {e}") from e
