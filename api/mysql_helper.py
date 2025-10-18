
import logging
import mysql.connector
from . import models
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)

@contextmanager
def get_mysql_connection(user, password, host, port, database):
    """Establishes a connection to the MySQL database and yields it."""
    connection = None
    try:
        connection = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        yield connection
    except mysql.connector.Error as e:
        raise RuntimeError(f"Error connecting to MySQL: {e}") from e
    finally:
        if connection:
            connection.close()

def get_mysql_schemas(details: models.MySQLConnectionDetails) -> list[str]:
    """Connects to a MySQL database and returns a list of schemas."""
    try:
        with get_mysql_connection(details.user, details.password, details.host, details.port, details.database) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT schema_name FROM information_schema.schemata ORDER BY schema_name")
            schemas = [row[0] for row in cursor]
            logging.info(f"Found {len(schemas)} MySQL schemas.")
            return schemas
    except mysql.connector.Error as e:
        raise RuntimeError(f"Error fetching schemas: {e}") from e

def list_mysql_objects(details: models.MySQLConnectionDetails, schema_name: str, object_type: str) -> list[str]:
    """Lists objects for a given schema and object type in MySQL."""
    # In MySQL, object types like 'TABLE', 'VIEW' are stored in the same namespace
    # and can be queried from information_schema.tables.
    # Stored procedures and functions are in information_schema.routines.
    
    query_map = {
        "TABLE": "SELECT table_name FROM information_schema.tables WHERE table_schema = %s AND table_type = 'BASE TABLE' ORDER BY table_name",
        "VIEW": "SELECT table_name FROM information_schema.tables WHERE table_schema = %s AND table_type = 'VIEW' ORDER BY table_name",
        "PROCEDURE": "SELECT routine_name FROM information_schema.routines WHERE routine_schema = %s AND routine_type = 'PROCEDURE' ORDER BY routine_name",
        "FUNCTION": "SELECT routine_name FROM information_schema.routines WHERE routine_schema = %s AND routine_type = 'FUNCTION' ORDER BY routine_name",
    }
    
    query = query_map.get(object_type.upper())
    if not query:
        raise ValueError(f"Unsupported object type for MySQL: {object_type}")

    try:
        with get_mysql_connection(details.user, details.password, details.host, details.port, details.database) as connection:
            cursor = connection.cursor()
            cursor.execute(query, (schema_name,))
            objects = [row[0] for row in cursor]
            return objects
    except mysql.connector.Error as e:
        raise RuntimeError(f"Error fetching objects from MySQL: {e}") from e

def get_mysql_ddl(details: models.MySQLConnectionDetails, schemas: list[str], object_types: list[str], object_names: list[str] | None = None, select_all: bool = False):
    """Extracts DDLs for specified schemas and object types from MySQL."""
    ddls = {obj_type: {} for obj_type in object_types}
    
    try:
        with get_mysql_connection(details.user, details.password, details.host, details.port, details.database) as connection:
            cursor = connection.cursor()
            
            for schema in schemas:
                for obj_type in object_types:
                    objects_to_fetch = []
                    if not object_names or select_all:
                        objects_to_fetch = list_mysql_objects(details, schema, obj_type)
                    else:
                        objects_to_fetch = object_names

                    for obj_name in objects_to_fetch:
                        try:
                            if obj_type.upper() in ['TABLE', 'VIEW']:
                                cursor.execute(f"SHOW CREATE {obj_type.upper()} `{schema}`.`{obj_name}`")
                                ddl_row = cursor.fetchone()
                                if ddl_row:
                                    # The DDL is in the second column
                                    ddl = ddl_row[1]
                                    key = f"{schema}.{obj_name}"
                                    ddls[obj_type][key] = ddl + ';'
                            elif obj_type.upper() in ['PROCEDURE', 'FUNCTION']:
                                cursor.execute(f"SHOW CREATE {obj_type.upper()} `{schema}`.`{obj_name}`")
                                ddl_row = cursor.fetchone()
                                if ddl_row:
                                    # The DDL is in the third column
                                    ddl = ddl_row[2]
                                    key = f"{schema}.{obj_name}"
                                    # Add DELIMITER statements for stored programs
                                    ddls[obj_type][key] = f"DELIMITER $$ {ddl} $$ DELIMITER ;"

                        except mysql.connector.Error as e:
                            logging.error(f"Error fetching DDL for {obj_type} '{obj_name}' in schema '{schema}': {e}")

        return ddls
    except mysql.connector.Error as e:
        raise RuntimeError(f"Error fetching DDL from MySQL: {e}") from e
