# Project Current State: spf-converter

This document provides an overview of the `spf-converter` project, detailing its current functionality, identifying areas that require attention, and proposing solutions.

## 1. Project Overview

The `spf-converter` project is a comprehensive tool designed to facilitate the migration of Oracle database objects (Stored Procedures/Functions, DDLs, and data) to PostgreSQL. It leverages AI (Ollama) for SQL conversion and schema comparison, RabbitMQ for asynchronous job processing, and a FastAPI backend with a Gradio user interface. Key features include:

*   **Oracle DDL Extraction:** Connects to Oracle to extract DDLs for various object types (tables, views, procedures, etc.).
*   **AI-Powered SQL/DDL Conversion:** Converts Oracle SQL (SPFs) and DDL statements to PostgreSQL syntax using Ollama.
*   **Schema Compatibility Comparison:** Uses AI to compare Oracle and PostgreSQL DDLs for migration compatibility.

*   **Data Migration:** Facilitates row-by-row data migration from Oracle tables to PostgreSQL.
*   **PostgreSQL SQL Execution:** Allows execution of SQL scripts against a PostgreSQL database, with verification capabilities.

*   **Job Management:** Tracks the status and results of all conversion, extraction, execution, and migration jobs.
*   **Gradio User Interface:** Provides an interactive web interface for all functionalities.
*   **OpenTelemetry Tracing:** Integrated for observability.

## 2. Working Components (What's Happening)

### 2.1. API (`api/` folder)

The `api/` folder contains the FastAPI backend, which is the core logic hub.

*   **`main.py`**: Initializes the FastAPI application, sets up tracing, and includes various routers. It also ensures RAG-related database tables are created on startup.
*   **`routes/`**: 
    *   **`conversion_routes.py`**: Handles API endpoints for converting Oracle SQL (SPFs) and DDLs. It creates jobs in the database and publishes messages to RabbitMQ for asynchronous processing.
    *   **`job_routes.py`**: Provides endpoints to retrieve job statuses, aggregate results for bulk conversions, and list paginated jobs by type.
    *   **`oracle_routes.py`**: Manages connections to Oracle, lists schemas and objects, and triggers DDL extraction.
    *   **`execution_routes.py`**: Offers endpoints to test PostgreSQL connections, create databases, and submit SQL files for execution against PostgreSQL. These are also processed asynchronously via RabbitMQ.
    *   **`migration_routes.py`**: Initiates data migration tasks. It performs schema compatibility checks (using AI), creates data migration jobs, fetches data from Oracle in batches, and queues individual rows for migration via RabbitMQ.

*   **`database.py`**: Manages PostgreSQL connection pools for the main application, verification, and RAG databases. It contains functions for creating and updating various job tables (`jobs`, `ddl_jobs`, `sql_execution_jobs`, `data_migration_jobs`, `documents`, `document_chunks`, `chat_history`), and utility functions for schema/table introspection.
*   **`ai_converter.py`**: Implements the core AI logic using Ollama for converting Oracle SPFs and DDLs to PostgreSQL. It also includes a function for AI-powered schema comparison.
*   **`sanitizer.py`**: Provides functions to clean and split SQL content, preparing it for execution or conversion.
*   **`queues.py`**: Defines RabbitMQ queue configurations (including Dead Letter Exchanges/Queues) and provides utilities for connecting to RabbitMQ and publishing messages.

*   **`tracing.py`**: Configures OpenTelemetry for distributed tracing, instrumenting the FastAPI application.
*   **`startup.py`**: Handles application startup tasks, including ensuring necessary PostgreSQL databases and users exist, initializing database connection pools, creating all required tables, and declaring RabbitMQ queues.
*   **`dependencies.py`**: Provides FastAPI dependencies, such as `get_current_user` for authentication.
*   **`migration_db.py`**: Contains functions related to database migration, including a migration for `sql_execution_jobs` table and `process_row_for_insertion` for data migration.
*   **`models.py`**: Defines Pydantic models for request/response validation and data structures across the API.
*   **`oracle_helper.py`**: Provides functions for connecting to Oracle, fetching schemas, listing objects, extracting DDLs using `DBMS_METADATA`, and fetching table data in batches.

### 2.2. Worker (`worker.py`)

The `worker.py` script acts as a RabbitMQ consumer, processing messages from various queues asynchronously.

*   **`sql_conversion_callback`**: Consumes messages from `conversion_jobs`. It performs Oracle SQL/DDL conversion using `ai_converter`, then publishes a new message to the `sql_execution_jobs` queue for verification.
*   **`sql_execution_callback`**: Consumes messages from `sql_execution_jobs`. It executes the provided SQL statements against a PostgreSQL database (either a dedicated verification DB or a user-specified one), updates the job status, and handles retries. It also updates the status of the original conversion job if it was a verification task.

*   **`data_migration_row_inserts_callback`**: Consumes messages from `data_migration_row_inserts`. It processes individual rows for insertion into the target PostgreSQL table, calling `migration_db.process_row_for_insertion`.
*   **Tracing**: Integrated with OpenTelemetry for tracing worker operations.

### 2.3. Verifier (`verifier/main.py`)

The `verifier/main.py` script is a separate process designed to poll the database for pending conversion jobs, process them, and verify the converted SQL.

*   It uses `ai_converter` for conversion and `verification.verify_procedure` for execution against a PostgreSQL database.
*   It includes logic to attempt self-correction with the LLM if initial verification fails.

### 2.4. UI (`app.py`, `ui/gradio_callbacks.py`, `ui/api_client.py`)

The user interface is built with Gradio.

*   **`app.py`**: Defines the Gradio application layout with multiple tabs for different functionalities (conversion, migration, DDL extraction, SQL execution, job monitoring, documentation).
*   **`ui/gradio_callbacks.py`**: Contains the Python functions that are triggered by Gradio UI events. These functions make HTTP requests to the FastAPI backend (`API_URL`) using `api_client.py` and update the Gradio components. It also includes polling logic for asynchronous job results.
*   **`ui/api_client.py`**: A utility module that encapsulates HTTP requests to the FastAPI backend, simplifying interaction from the Gradio frontend.

## 3. Not Working Now / Areas for Improvement

1.  **Redundant Conversion/Verification Logic (`verifier/main.py` vs. `worker.py`):**
    *   **Issue:** The `verifier/main.py` script polls for pending jobs and performs conversion/verification, which largely duplicates the functionality of the `worker.py`'s `sql_conversion_callback` and `sql_execution_callback` that operate via RabbitMQ. This creates two separate, potentially conflicting, job processing flows.
    *   **Impact:** Inconsistent job processing, potential race conditions, and increased complexity.
2.  **Incomplete Schema Comparison (`api/schema_comparer.py`):**
    *   **Issue:** The `api/schema_comparer.py` file contains commented-out code for `sqlcompyre` and placeholder functions. The project currently relies solely on `ai_converter.compare_schemas_with_ollama_ai` for schema comparison.
    *   **Impact:** The `schema_comparer.py` file is either dead code or an incomplete feature, leading to confusion and unused dependencies if `sqlcompyre` was intended.
3.  **Missing `log_migration_row_status` Implementation:**
    *   **Issue:** The `api/database.py` file has a `log_migration_row_status` function with a comment stating "This function is called in worker.py but its implementation is missing."
    *   **Impact:** Row-level status tracking for data migration is not properly implemented, making it difficult to monitor granular progress or identify specific row failures.
4.  **Inconsistent Data Migration Callbacks in `worker.py`:**
    *   **Issue:** `worker.py` has a `data_migration_row_callback` marked as `TODO`, while `data_migration_row_inserts_callback` seems to be the active handler for row insertions.
    *   **Impact:** The `data_migration_row_callback` is likely a leftover or misnamed, causing confusion.
5.  **Missing `execute_ddl_statement` in `api/migration_db.py`:**
    *   **Issue:** The `worker.py`'s `data_migration_row_inserts_ddl_callback` attempts to call `migration_db.execute_ddl_statement`, but this function is not defined in `api/migration_db.py`.
    *   **Impact:** DDL execution for data migration (if intended to be separate from general SQL execution) will fail.
6.  **Fragile Ollama Model Name Determination:**
    *   **Issue:** `api/ai_converter.py`'s `get_running_model_name` relies on `ollama.ps()`, with a comment noting potential inconsistencies in its output across Ollama versions.
    *   **Impact:** The system might fail to correctly identify a running Ollama model, leading to conversion failures.
7.  **Potential SQL Splitting Limitations:**
    *   **Issue:** `api/routes/conversion_routes.py`'s `_split_sql_procedures` and `api/sanitizer.py`'s `sanitize_for_execution` use regex and `sqlparse` for splitting Oracle SQL. Comments suggest this might not be robust enough for all Oracle dialects.
    *   **Impact:** Complex or unusual Oracle SQL scripts might not be correctly parsed and converted.
8.  **Inefficient Job Retrieval:**
    *   **Issue:** `api/database.py`'s `get_job` and `get_jobs_by_ids` iterate through multiple job tables to find a job.
    *   **Impact:** This approach can be inefficient, especially with a growing number of job types and tables.
9.  **Broad Database Privileges in Startup:**
    *   **Issue:** `api/startup.py` uses `GRANT ALL PRIVILEGES ON DATABASE ... TO ...` during database initialization.
    *   **Impact:** While convenient for development, granting `ALL PRIVILEGES` is generally not recommended for production environments due to security concerns.
10. **Duplicated `get_git_info` Function:**
    *   **Issue:** The `get_git_info` function is present in both `app.py` and `ui/gradio_callbacks.py`.
    *   **Impact:** Code duplication, making maintenance harder.

## 4. How to Fix It (Proposed Solutions)

1.  **Consolidate Conversion/Verification Logic:**
    *   **Action:** Remove `verifier/main.py`. Ensure all conversion and verification flows are handled exclusively through the RabbitMQ worker (`worker.py`). The `sql_conversion_callback` should be responsible for initiating conversion and then queuing the result for `sql_execution_callback` (verification). The `sql_execution_callback` should then update the status of the *original* conversion job based on verification success or failure.
2.  **Address `api/schema_comparer.py`:**
    *   **Action:** Decide whether `sqlcompyre` is a desired feature. If not, delete `api/schema_comparer.py` to remove dead code. If it is, fully implement the placeholder functions and integrate `sqlcompyre` comparison into the migration flow as an alternative or supplementary check to the AI comparison.
3.  **Implement `log_migration_row_status`:**
    *   **Action:** Add the missing implementation for `log_migration_row_status` in `api/database.py`. This could involve creating a new `data_migration_row_statuses` table or updating aggregated counts/error flags in the `data_migration_jobs` table.
4.  **Clean Up Data Migration Callbacks in `worker.py`:**
    *   **Action:** Remove the `data_migration_row_callback` `TODO` function. Ensure `data_migration_row_inserts_callback` is correctly handling all row insertion logic.
5.  **Define `execute_ddl_statement`:**
    *   **Action:** Implement `execute_ddl_statement` in `api/migration_db.py` if DDL execution is intended to be part of the data migration process. This function should take a DDL statement and execute it against the target PostgreSQL database.
6.  **Improve Ollama Model Name Determination:**
    *   **Action:** Enhance `api/ai_converter.py`'s `get_running_model_name` to be more robust, perhaps by iterating through `ollama.list()` and checking for a specific model name, or by providing a clear configuration option for the user to specify the model name in `.env`.
7.  **Refine SQL Splitting:**
    *   **Action:** Research and implement a more robust Oracle SQL parser or a more sophisticated splitting logic in `_split_sql_procedures` and `sanitize_for_execution` to handle complex Oracle constructs (e.g., anonymous blocks, nested procedures, different terminators).
8.  **Centralize Job Tracking:**
    *   **Action:** Consider refactoring the job tracking mechanism in `api/database.py`. A single `jobs` table with a `job_type` column and a `details` JSONB column could store all job-specific metadata, simplifying `get_job` and `get_jobs_by_ids` queries.
9.  **Refine Database Privileges:**
    *   **Action:** For production deployments, review `api/startup.py` and replace `GRANT ALL PRIVILEGES` with more granular permissions (e.g., `GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ... TO ...`).
10. **Remove Duplicated `get_git_info` Function:**
    *   **Action:** Remove the `get_git_info` function from `app.py`. Ensure `ui/gradio_callbacks.py` is the sole location for this utility function, and `app.py` calls it from there.
