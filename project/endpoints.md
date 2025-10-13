# Exposed Endpoints

This document outlines the API endpoints exposed by the application.

## Health Check

### `GET /health`

*   **Description:** A simple health check endpoint to verify that the API is running.
*   **File:** `api/main.py`

## Conversion Endpoints

These endpoints are for converting Oracle SQL to PostgreSQL.

### `POST /convert`

*   **Description:** Submits a single Oracle stored procedure or SQL block for conversion to PostgreSQL.
*   **File:** `api/routes/conversion_routes.py`

### `POST /convert-file`

*   **Description:** Uploads a `.sql` file containing multiple Oracle stored procedures or SQL blocks for conversion.
*   **File:** `api/routes/conversion_routes.py`

### `POST /convert-ddl`

*   **Description:** Submits a single Oracle DDL statement for conversion to PostgreSQL.
*   **File:** `api/routes/conversion_routes.py`

### `POST /convert-ddl-file`

*   **Description:** Uploads a `.sql` file containing multiple Oracle DDL statements for conversion.
*   **File:** `api/routes/conversion_routes.py`

### `POST /reconvert-with-suggestions`

*   **Description:** Resubmits a previously failed conversion job with new suggestions or modifications to the original SQL.
*   **File:** `api/routes/conversion_routes.py`

## Document and RAG Endpoints

These endpoints are for managing documents and interacting with the RAG (Retrieval-Augmented Generation) model.

### `POST /documents/upload`

*   **Description:** Uploads one or more PDF documents to be processed and used by the RAG model.
*   **File:** `api/routes/document_routes.py`

### `GET /documents`

*   **Description:** Lists all the documents that have been uploaded by the current user.
*   **File:** `api/routes/document_routes.py`

### `POST /chat`

*   **Description:** Sends a query to the RAG model to get a response based on the content of the uploaded documents.
*   **File:** `api/routes/document_routes.py`

### `GET /chat/history/{user_id}/{conversation_id}`

*   **Description:** Retrieves the chat history for a specific user and conversation.
*   **File:** `api/routes/document_routes.py`

## SQL Execution Endpoints

These endpoints are for executing SQL against a PostgreSQL database.

### `POST /test-postgres-connection`

*   **Description:** Tests the connection to a PostgreSQL database using the provided credentials.
*   **File:** `api/routes/execution_routes.py`

### `POST /create-database`

*   **Description:** Creates a new database in the PostgreSQL server.
*   **File:** `api/routes/execution_routes.py`

### `POST /execute-sql`

*   **Description:** Uploads and executes a `.sql` file on the specified PostgreSQL database.
*   **File:** `api/routes/execution_routes.py`

## Job Status Endpoints

These endpoints are for checking the status and results of various jobs.

### `GET /jobs/types`

*   **Description:** Returns a list of all available job types.
*   **File:** `api/routes/job_routes.py`

### `GET /jobs/job/{job_id}`

*   **Description:** Retrieves the status and details of a specific job by its ID.
*   **File:** `api/routes/job_routes.py`

### `POST /jobs/aggregate`

*   **Description:** Aggregates the results of multiple conversion jobs into a single response.
*   **File:** `api/routes/job_routes.py`

### `GET /jobs/{table_name}`

*   **Description:** Retrieves a paginated list of jobs from a specific job table.
*   **File:** `api/routes/job_routes.py`

### `GET /jobs/job/{job_id}/result`

*   **Description:** Retrieves the final result of a completed DDL conversion job, typically as a downloadable SQL file.
*   **File:** `api/routes/job_routes.py`

### `GET /jobs/job/{parent_job_id}/children`

*   **Description:** Retrieves the status of all child jobs associated with a parent DDL extraction job.
*   **File:** `api/routes/job_routes.py`

### `GET /jobs/sql-execution-job/{job_id}`

*   **Description:** Retrieves the status and results of a SQL execution job.
*   **File:** `api/routes/job_routes.py`

## Data Migration Endpoints

These endpoints are for managing the data migration process from Oracle to PostgreSQL.

### `POST /migrate/start`

*   **Description:** Starts a data migration process from an Oracle table to a PostgreSQL table.
*   **File:** `api/routes/migration_routes.py`

### `GET /migrate/status/{job_id}`

*   **Description:** Checks the status of an ongoing data migration job.
*   **File:** `api/routes/migration_routes.py`

### `POST /oracle/schemas`

*   **Description:** Retrieves a list of all schemas from the connected Oracle database.
*   **File:** `api/routes/migration_routes.py`

### `POST /oracle/schemas/{schema_name}/tables`

*   **Description:** Retrieves a list of all tables within a specific schema in the Oracle database.
*   **File:** `api/routes/migration_routes.py`

### `POST /postgres/schemas`

*   **Description:** Retrieves a list of all schemas from the connected PostgreSQL database.
*   **File:** `api/routes/migration_routes.py`

### `POST /postgres/schemas/{schema_name}/tables`

*   **Description:** Retrieves a list of all tables within a specific schema in the PostgreSQL database.
*   **File:** `api/routes/migration_routes.py`

### `POST /oracle/schemas/{schema_name}/tables/{table_name}/ddl`

*   **Description:** Retrieves the DDL for a specific table in the Oracle database.
*   **File:** `api/routes/migration_routes.py`

### `POST /postgres/schemas/{schema_name}/tables/{table_name}/ddl`

*   **Description:** Retrieves the DDL for a specific table in the PostgreSQL database.
*   **File:** `api/routes/migration_routes.py`

## Oracle Metadata Endpoints

These endpoints are for interacting with and extracting metadata from an Oracle database.

### `POST /connect`

*   **Description:** Connects to an Oracle database and retrieves a list of schemas.
*   **File:** `api/routes/oracle_routes.py`

### `POST /test-extraction`

*   **Description:** Tests the DDL extraction process from the Oracle database to ensure it's working correctly.
*   **File:** `api/routes/oracle_routes.py`

### `POST /list-objects`

*   **Description:** Lists all objects (e.g., tables, procedures) of a specific type within a given schema in the Oracle database.
*   **File:** `api/routes/oracle_routes.py`

### `POST /extract`

*   **Description:** Extracts the DDL for specified objects from the Oracle database.
*   **File:** `api/routes/oracle_routes.py`
