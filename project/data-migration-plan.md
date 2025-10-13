## Strategic Plan: Understanding Current Data Migration Logic

### 1. Understanding the Goal

The objective is to thoroughly understand the current end-to-end data migration logic within the project, specifically focusing on the process of migrating data from Oracle to PostgreSQL. This includes identifying how schema comparison is performed (especially with AI involvement), how data is transferred, and how the overall process is managed and tracked.

### 2. Investigation & Analysis

To achieve a comprehensive understanding, I will perform the following investigative steps:

*   **Re-examine `api/routes/migration_routes.py`:**
    *   Focus on the `start_migration` endpoint to trace the initial synchronous flow of a data migration request.
    *   Identify all direct function calls made from this endpoint and their immediate purpose.
*   **Deep Dive into Schema Comparison:**
    *   **`api/ai_converter.py`:** Analyze the `compare_schemas_with_ollama_ai` function.
        *   Understand its inputs (`oracle_ddl`, `postgres_ddl`, `data_migration_mode`).
        *   Examine how the `data_migration_mode` flag alters the prompt sent to Ollama, specifically for column name comparison versus comprehensive schema comparison.
        *   Determine the expected JSON output structure from Ollama (`is_compatible`, `issues`) and how the system interprets it.
    *   **`api/schema_comparer.py`:** Review this file again to confirm that its commented-out sections and placeholder functions are indeed inactive in the current data migration flow, or if any active parts contribute to schema understanding.
*   **Oracle Database Interaction:**
    *   **`api/oracle_helper.py`:** Investigate functions related to:
        *   Connecting to Oracle.
        *   `get_oracle_table_ddl`: How it extracts DDL for a given table.
        *   Any functions responsible for reading actual data from Oracle tables.
*   **PostgreSQL Database Interaction:**
    *   **`api/database.py`:** Examine functions related to:
        *   Connecting to PostgreSQL.
        *   `get_postgres_table_ddl`: How it extracts DDL for a given table.
        *   Any functions responsible for writing actual data into PostgreSQL tables.
    *   **`api/migration_db.py`:** Analyze functions for:
        *   `create_migration_job`: How a new migration job record is initiated.
        *   `update_migration_job_status`: How the status of a migration job is tracked and updated throughout its lifecycle.
        *   `get_migration_job`: How job details are retrieved.
*   **Asynchronous Processing and Worker Logic:**
    *   **`api/queues.py`:** Understand the queue configurations and how messages are published to RabbitMQ for migration jobs.
    *   **`worker.py`:** This is critical. I will need to infer its behavior by searching for its main loop or job processing function.
        *   How does it consume messages from RabbitMQ?
        *   What steps does it take to process a migration job (e.g., calling AI converter, performing data transfer)?
        *   How does it interact with `api/oracle_helper.py` and `api/database.py` for data extraction and insertion?
        *   How does it update the job status via `migration_db.py`?
*   **Verification and Error Handling:**
    *   **`api/verification.py`:** Determine if and how `verify_procedure` or `verify_procedure_with_creds` are used within the data migration flow (e.g., to verify converted DDL or data insertion statements).
    *   Identify error handling mechanisms (`try-except` blocks, HTTPException) across all relevant files to understand how failures are managed and reported.

**Critical Questions to Answer:**

1.  What is the precise sequence of operations from the `start_migration` API call to the completion of data transfer?
2.  How are Oracle and PostgreSQL DDLs obtained for schema comparison?
3.  What is the exact role of Ollama (AI) in schema comparison for data migration, and how does the `data_migration_mode` parameter specifically modify its behavior?
4.  How are migration jobs persisted and their states updated throughout the process?
5.  What is the mechanism for extracting data from Oracle and inserting it into PostgreSQL? Is it a bulk operation, row-by-row, or batched?
6.  Are there any data transformation rules applied during the transfer, and if so, where are they defined?
7.  How are errors (e.g., database connection issues, AI response failures, data transfer errors) handled and communicated back to the user or logged?

### 3. Proposed Strategic Approach

**Phase 1: Synchronous API Request Processing**
*   **Action:** Trace the execution path within `api/routes/migration_routes.py` from the `start_migration` endpoint.
*   **Output:** A detailed flow diagram or step-by-step description of:
    1.  Input validation of `DataMigrationRequest`.
    2.  Fetching Oracle DDL using `oracle_helper.get_oracle_table_ddl`.
    3.  Fetching PostgreSQL DDL using `database.get_postgres_table_ddl`.
    4.  Invoking `ai_converter.compare_schemas_with_ollama_ai` with `data_migration_mode=True`.
    5.  Handling the `is_compatible` and `issues` response from the AI.
    6.  Creating a migration job record in PostgreSQL using `migration_db.create_migration_job`.
    7.  Publishing a message to RabbitMQ via `queues.get_rabbitmq_connection` and `channel.basic_publish`.
    8.  Updating the job status to "SUBMITTED" using `migration_db.update_migration_job_status`.
    9.  Returning a `job_id` to the client.

**Phase 2: Asynchronous Worker Processing**
*   **Action:** Investigate `worker.py` to understand how it consumes and processes migration jobs.
*   **Output:** A description of the worker's lifecycle:
    1.  How the worker connects to RabbitMQ and consumes messages.
    2.  How it retrieves job details from `migration_db` using the `job_id` from the message.
    3.  The sequence of operations for actual data transfer:
        *   Connecting to Oracle (using credentials from job details).
        *   Extracting data from the source Oracle table.
        *   Connecting to PostgreSQL (using credentials from job details).
        *   Inserting data into the destination PostgreSQL table.
        *   Any intermediate data processing or transformation.
    4.  How `migration_db.update_migration_job_status` is used to reflect progress (e.g., "IN_PROGRESS", "COMPLETED", "FAILED").
    5.  The role of `api/verification.py` if any, in verifying the transferred data or DDL.

**Phase 3: Error Handling and Logging**
*   **Action:** Analyze error handling (`try-except` blocks) and logging statements across all identified components.
*   **Output:** A summary of:
    1.  How exceptions are caught and what information is logged.
    2.  How errors impact job status updates in `migration_db`.
    3.  Mechanisms for reporting errors back to the user (e.g., via API responses for synchronous parts, or job status for asynchronous parts).

### 4. Verification Strategy

The success of this strategic plan will be measured by the clarity, accuracy, and completeness of the resulting explanation of the data migration logic.

*   **Completeness Check:** Ensure all stages of the migration (initiation, schema comparison, job tracking, data transfer, status updates) are covered.
*   **Accuracy Check:** Verify that the described interactions between modules and functions align with the code's actual behavior.
*   **Clarity Check:** The explanation should be easy to follow, logically structured, and free of ambiguity.
*   **AI Role Clarity:** Specifically confirm that the explanation clearly delineates when and how AI is used, and how its behavior is modified for data migration versus other functionalities.

### 5. Anticipated Challenges & Considerations

*   **Implicit Logic in `worker.py`:** Without direct execution, understanding the exact data transfer mechanism within `worker.py` might require careful inference from imports and function calls. The actual data extraction/insertion logic might be encapsulated in helper functions not immediately obvious.
*   **Dynamic DDL Generation/Fetching:** The placeholder functions in `api/schema_comparer.py` suggest that the actual DDL fetching might be more complex or dynamic, relying on `oracle_helper.py` and `database.py`. I need to ensure I capture the real implementation.
*   **Data Type Conversion:** While the AI's role in data migration is narrowed to column names, the actual data transfer process will inevitably involve data type conversions between Oracle and PostgreSQL. I need to identify where this logic resides and how it's handled.
*   **Scalability and Batching:** The use of RabbitMQ suggests potential for large-scale data migration. I need to look for clues on how data is batched or streamed during transfer to avoid memory issues.
*   **Transaction Management:** Understanding how transactions are managed during data transfer (e.g., atomicity of inserts) is crucial for data integrity.
*   **External Dependencies:** The reliance on Ollama and RabbitMQ means their operational status is critical for the entire migration process. The current error highlights this.