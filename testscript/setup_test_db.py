
import oracledb
import os
import requests
import sys
import re

# --- Configuration ---
API_URL = "http://127.0.0.1:8000"
DB_USER = "newuser"
DB_PASSWORD = os.environ.get("ORACLE_SYSTEM_PASSWORD", "password")
DB_HOST = "192.168.106.2"
DB_PORT = 1521
DB_SERVICE_NAME = "xe"

# New user details
NEW_USER = "DEMOARUL"
NEW_USER_PASSWORD = "password"

# SQL files to execute
SQL_FILES = [
    "sql-assests/airline_schema.sql",
    "sql-assests/airline_data.sql",
    "sql-assests/airline_sprocs.sql"
]

EXPECTED_TABLES = [
    "COUNTRIES", "AIRPORTS", "AIRLINES", "AIRCRAFT", "FLIGHTS", 
    "PASSENGERS", "BOOKINGS", "BOARDING_PASSES", "EMPLOYEES", "FLIGHT_CREW"
]

def execute_sql_from_file(cursor, filepath):
    """Reads and executes SQL statements from a file."""
    print(f"Executing SQL from {filepath}...")
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            # Remove all -- style comments
            content = re.sub(r'--.*\n', '\n', content)

            # Use slash separator for procedures, semicolon for others
            if "sprocs" in filepath:
                statements = re.split(r'\n/\s*\n', content)
            else:
                statements = content.split(';')

            for statement in statements:
                statement = statement.strip()
                if statement:
                    try:
                        cursor.execute(statement)
                    except oracledb.Error as e:
                        print(f"  -> Failed to execute statement: {statement[:70]}...")
                        print(f"  -> Error: {e}")
    except FileNotFoundError:
        print(f"  -> ERROR: SQL file not found at {filepath}")
        sys.exit(1)

def verify_setup():
    """Calls the API to verify that the tables were created successfully."""
    print("\n--- Starting Verification Step ---")
    connection_details = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": NEW_USER,
        "password": NEW_USER_PASSWORD,
        "service_name": DB_SERVICE_NAME
    }
    payload = {
        "connection_details": connection_details,
        "schema_name": NEW_USER.upper(),
        "object_type": "TABLE",
    }
    try:
        print(f"Calling API to list tables for schema '{NEW_USER.upper()}'...")
        response = requests.post(f"{API_URL}/list-objects", json=payload)
        response.raise_for_status()
        data = response.json()
        listed_objects = data.get("objects", [])
        print(f"API returned {len(listed_objects)} tables.")

        missing_tables = [t for t in EXPECTED_TABLES if t not in listed_objects]

        if not missing_tables:
            print("\n[SUCCESS] Verification complete. All expected tables were found.")
        else:
            print("\n[FAILURE] Verification failed. The following tables are missing:")
            for table in missing_tables:
                print(f"  - {table}")
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"\n[FAILURE] Verification failed. Could not connect to the application API at {API_URL}.")
        print(f"Error: {e}")
        print("Please ensure the main application is running before executing this script.")
        sys.exit(1)

def main():
    """Main function to create user, grant privileges, and populate schema."""
    system_conn = None
    try:
        dsn = oracledb.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE_NAME)
        system_conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn)
        system_cursor = system_conn.cursor()
        print(f"Successfully connected as SYSTEM to PDB: {DB_SERVICE_NAME}.")

        # Drop the user to ensure a clean slate
        try:
            print(f"Dropping user '{NEW_USER}' to ensure a clean slate...")
            system_cursor.execute(f"DROP USER {NEW_USER} CASCADE")
            print(f"User '{NEW_USER}' dropped successfully.")
        except oracledb.Error as e:
            # ORA-01918: user does not exist
            if "ORA-01918" in str(e):
                print(f"User '{NEW_USER}' does not exist. Skipping drop.")
            else:
                raise

        print(f"Creating user '{NEW_USER}'...")
        system_cursor.execute(f"CREATE USER {NEW_USER} IDENTIFIED BY {NEW_USER_PASSWORD}")
        print(f"User '{NEW_USER}' created successfully.")

        print(f"Granting privileges to '{NEW_USER}'...")
        system_cursor.execute(f"GRANT DBA TO {NEW_USER}")
        system_cursor.execute(f"GRANT CREATE SESSION, UNLIMITED TABLESPACE TO {NEW_USER}")
        print("Privileges granted successfully.")

    except oracledb.Error as e:
        print(f"Error during database setup: {e}")
        if system_conn:
            system_conn.close()
        sys.exit(1)
    finally:
        if system_conn:
            system_conn.close()

    # --- Connect as the new user and populate schema ---
    new_user_conn = None
    try:
        dsn = oracledb.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE_NAME)
        new_user_conn = oracledb.connect(user=NEW_USER, password=NEW_USER_PASSWORD, dsn=dsn)
        new_user_cursor = new_user_conn.cursor()
        print(f"\nSuccessfully connected as new user '{NEW_USER}'.")

        for sql_file in SQL_FILES:
            execute_sql_from_file(new_user_cursor, sql_file)

        new_user_conn.commit()
        print("\nDatabase setup complete!")

    except oracledb.Error as e:
        print(f"Error connecting as '{NEW_USER}' or populating schema: {e}")
        if new_user_conn:
            new_user_conn.close()
        sys.exit(1)
    finally:
        if new_user_conn:
            new_user_conn.close()
    
    # --- Verify Setup ---
    verify_setup()

if __name__ == "__main__":
    main()
