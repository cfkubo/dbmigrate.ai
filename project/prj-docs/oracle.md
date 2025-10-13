# Oracle Manual Validation Workflow

This document provides a manual workflow to validate the Oracle database setup and DDL extraction process using SQL queries. This can be executed using a tool like SQL Developer or SQL*Plus.

## 1. User Creation and Privileges

This section covers how to create a user and grant the necessary privileges for the DDL extraction process.

### Create a New User

First, connect to the database as a user with administrative privileges (like `SYS` or `SYSTEM`). Then, execute the following command to create a new user. Replace `new_user` and `password` with your desired username and password.

```sql
CREATE USER migrator IDENTIFIED BY password;
```

### Grant Privileges

For the DDL extraction to work, the user needs extensive privileges. Granting the `DBA` role is the most straightforward way to ensure all necessary permissions are present.

```sql
GRANT DBA TO migrator;
```

If you want to grant more granular privileges instead of `DBA`, the user will need at least the following:
- `CREATE SESSION`
- `SELECT ANY DICTIONARY` or `SELECT_CATALOG_ROLE`
- `SELECT` on `DBA_OBJECTS` and `DBA_USERS`

```sql
GRANT CREATE SESSION TO migrator;
GRANT SELECT ANY DICTIONARY TO migrator;
-- Or, if SELECT ANY DICTIONARY is too broad:
-- GRANT SELECT_CATALOG_ROLE TO new_user;

GRANT SELECT ON DBA_OBJECTS TO migrator;
GRANT SELECT ON DBA_USERS TO migrator;
```

## 2. Viewing Database Objects

Once the user is created and has the necessary privileges, you can connect as that user and inspect the database objects.

### List All Schemas

To see all the schemas (users) in the database, you can query the `dba_users` view.

```sql
SELECT username FROM dba_users ORDER BY username;
```

### List Objects in a Specific Schema

To view all objects (tables, procedures, etc.) within a specific schema, you can query the `dba_objects` view. Replace `SCHEMA_NAME` with the name of the schema you want to inspect.

```sql
SELECT object_name, object_type, owner
FROM dba_objects
WHERE owner = 'SCHEMA_NAME'
ORDER BY object_type, object_name;
```

For example, to see all objects in the `DEMOARUL` schema:

```sql
SELECT object_name, object_type, owner
FROM dba_objects
WHERE owner = 'DEMOARUL'
ORDER BY object_type, object_name;
```

If you are connected as `DEMOARUL` and still cannot see tables, it might be because there are no tables in that schema, or the user does not have the correct privileges to view them (if not granted `DBA` or `SELECT ANY DICTIONARY`).

## 3. Testing DDL Extraction

This section provides queries to test the DDL extraction functionality directly in your SQL tool.

### Configure DBMS_METADATA

The `DBMS_METADATA` package is used to extract DDLs. You can configure its output format. The following settings are recommended for cleaner output, but as we've seen, they can sometimes trigger database bugs.

```sql
-- Optional: These settings can help produce cleaner DDL, but may cause issues on some DB versions.
BEGIN
    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'STORAGE', FALSE);
    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SEGMENT_ATTRIBUTES', FALSE);
    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SQLTERMINATOR', TRUE);
    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'PRETTY', TRUE);
    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'CONSTRAINTS_AS_ALTER', FALSE);
    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'REF_CONSTRAINTS', TRUE);
    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'EMIT_SCHEMA', FALSE);
END;
/
```

### Extract DDL for a Specific Object

You can use the `DBMS_METADATA.GET_DDL` function to extract the DDL for a specific object.

```sql
-- Set the output to be long enough to display the full DDL
SET LONG 2000000
SET PAGESIZE 0

-- Extract the DDL for a table
SELECT DBMS_METADATA.GET_DDL('TABLE', 'TABLE_NAME', 'SCHEMA_NAME') FROM DUAL;

-- Extract the DDL for a procedure
SELECT DBMS_METADATA.GET_DDL('PROCEDURE', 'PROCEDURE_NAME', 'SCHEMA_NAME') FROM DUAL;
```

For example, to get the DDL for the `AIRCRAFT` table in the `DEMOARUL` schema:

```sql
SET LONG 2000000
SET PAGESIZE 0
SELECT DBMS_METADATA.GET_DDL('TABLE', 'AIRCRAFT', 'DEMOARUL') FROM DUAL;
```

If this query results in an `ORA-00600` error, it confirms that the issue is with the Oracle database itself and not with the Python application. If it works, there might be a more subtle issue in the interaction between the Python driver and the database.
