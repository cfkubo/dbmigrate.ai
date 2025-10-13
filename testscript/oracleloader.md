
# Oracle Test Schema Loader (`setup_test_db.py`)

This script is a utility to create a clean, isolated Oracle schema for end-to-end testing of the SPF Converter application. It is designed to be run from the root of the project directory.

## Purpose

The primary goal of this script is to automate the setup of a dedicated test user and schema. This ensures that testing is performed on a known, consistent database state, which helps in reliably reproducing and diagnosing issues related to database metadata extraction and conversion.

The script performs the following actions:

1.  Connects to the Oracle database using the `SYSTEM` user.
2.  Creates a new database user/schema named `arul_oracaledb`.
3.  Grants this new user the necessary privileges (e.g., `CONNECT`, `RESOURCE`, `CREATE VIEW`, `CREATE PROCEDURE`).
4.  Connects to the database as the new `arul_oracaledb` user.
5.  Executes a series of SQL scripts to create the database objects (tables, data, and stored procedures).

## Configuration

Before running the script, you must configure the password for the `SYSTEM` user by setting an environment variable.

-   **`ORACLE_SYSTEM_PASSWORD`**: The password for your Oracle `SYSTEM` user.

Set it in your terminal like this:

```bash
export ORACLE_SYSTEM_PASSWORD='your_actual_system_password'
```

## How to Run

Once the environment variable is set, you can execute the script from the **root of the project directory** using Python:

```bash
python3 testscript/setup_test_db.py
```

## Script Details

-   **New User Created**: `arul_oracaledb`
-   **New User Password**: `password` (This is a placeholder and can be changed in the script if needed).
-   **SQL Files Executed**: The script executes the following files from the `sql-assests/` directory in order:
    1.  `airline_schema.sql` - Creates the table structures.
    2.  `airline_data.sql` - Populates the tables with sample data.
    3.  `airline_sprocs.sql` - Creates stored procedures.

Upon successful completion, you will have a new schema ready for testing the application's database connectivity and metadata extraction features.
