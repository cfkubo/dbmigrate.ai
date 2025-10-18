
import logging
import ibm_db
from . import models
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)

@contextmanager
def get_db2_connection(database, hostname, port, protocol, uid, pwd):
    """Establishes a connection to the DB2 database and yields it."""
    connection = None
    try:
        conn_str = (
            f"DATABASE={database};"
            f"HOSTNAME={hostname};"
            f"PORT={port};"
            f"PROTOCOL={protocol};"
            f"UID={uid};"
            f"PWD={pwd};"
        )
        connection = ibm_db.connect(conn_str, "", "")
        yield connection
    except Exception as e:
        raise RuntimeError(f"Error connecting to DB2: {e}") from e
    finally:
        if connection:
            ibm_db.close(connection)

def get_db2_schemas(details: models.DB2ConnectionDetails) -> list[str]:
    """Connects to a DB2 database and returns a list of schemas."""
    try:
        with get_db2_connection(details.database, details.hostname, details.port, details.protocol, details.uid, details.pwd) as connection:
            stmt = ibm_db.exec_immediate(connection, "SELECT schemaname FROM SYSCAT.SCHEMATA ORDER BY schemaname")
            schemas = []
            result = ibm_db.fetch_tuple(stmt)
            while result:
                schemas.append(result[0])
                result = ibm_db.fetch_tuple(stmt)
            logging.info(f"Found {len(schemas)} DB2 schemas.")
            return schemas
    except Exception as e:
        raise RuntimeError(f"Error fetching schemas: {e}") from e

def list_db2_objects(details: models.DB2ConnectionDetails, schema_name: str, object_type: str) -> list[str]:
    """Lists objects for a given schema and object type in DB2."""
    query_map = {
        "TABLE": "SELECT tabname FROM SYSCAT.TABLES WHERE tabschema = ? AND type = 'T' ORDER BY tabname",
        "VIEW": "SELECT tabname FROM SYSCAT.TABLES WHERE tabschema = ? AND type = 'V' ORDER BY tabname",
        "PROCEDURE": "SELECT routinename FROM SYSCAT.ROUTINES WHERE routineschema = ? AND routinetype = 'P' ORDER BY routinename",
        "FUNCTION": "SELECT routinename FROM SYSCAT.ROUTINES WHERE routineschema = ? AND routinetype = 'F' ORDER BY routinename",
    }
    
    query = query_map.get(object_type.upper())
    if not query:
        raise ValueError(f"Unsupported object type for DB2: {object_type}")

    try:
        with get_db2_connection(details.database, details.hostname, details.port, details.protocol, details.uid, details.pwd) as connection:
            stmt = ibm_db.prepare(connection, query)
            ibm_db.bind_param(stmt, 1, schema_name)
            ibm_db.execute(stmt)
            objects = []
            result = ibm_db.fetch_tuple(stmt)
            while result:
                objects.append(result[0])
                result = ibm_db.fetch_tuple(stmt)
            return objects
    except Exception as e:
        raise RuntimeError(f"Error fetching objects from DB2: {e}") from e

def get_db2_ddl(details: models.DB2ConnectionDetails, schemas: list[str], object_types: list[str], object_names: list[str] | None = None, select_all: bool = False):
    """Extracts DDLs for specified schemas and object types from DB2."""
    ddls = {obj_type: {} for obj_type in object_types}
    # Note: Getting DDL from DB2 can be complex and may require specific stored procedures
    # or reconstructing from system catalog tables. This is a simplified placeholder.
    logging.warning("DB2 DDL extraction is a simplified placeholder and may not work in all environments.")
    
    try:
        with get_db2_connection(details.database, details.hostname, details.port, details.protocol, details.uid, details.pwd) as connection:
            for schema in schemas:
                for obj_type in object_types:
                    objects_to_fetch = []
                    if not object_names or select_all:
                        objects_to_fetch = list_db2_objects(details, schema, obj_type)
                    else:
                        objects_to_fetch = object_names

                    for obj_name in objects_to_fetch:
                        # This is a placeholder. A more robust solution would be needed here.
                        ddl = f"-- DDL for {obj_type} {schema}.{obj_name} could not be automatically extracted."
                        key = f"{schema}.{obj_name}"
                        ddls[obj_type][key] = ddl
        return ddls
    except Exception as e:
        raise RuntimeError(f"Error fetching DDL from DB2: {e}") from e
