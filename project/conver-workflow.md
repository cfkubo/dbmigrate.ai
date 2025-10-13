# SPF and DDL Conversion Workflow

This document outlines the end-to-end workflow for converting Oracle Stored Procedures (SPF) and Data Definition Language (DDL) scripts to their PostgreSQL equivalents using the DbMigrate.AI application.

The system is designed asynchronously, utilizing a FastAPI backend, a Gradio user interface, a RabbitMQ message queue, and a separate worker process to handle the heavy lifting of AI-based code conversion.

## High-Level Architecture

1.  **Frontend (UI)**: A Gradio web interface (`app.py`) provides the user with input forms for their Oracle code.
2.  **Backend (API)**: A FastAPI application (`api/`) receives requests from the frontend, creates conversion jobs, and queues them for processing.
3.  **Message Queue**: RabbitMQ is used to decouple the API from the conversion process, managing the queue of pending jobs.
4.  **Worker**: A Python process (`worker.py`) consumes jobs from the queue, orchestrates the conversion with an AI model, verifies the output, and updates the job status in the database.
5.  **Database**: A database (likely PostgreSQL) stores job information, including status, original code, converted code, and any errors.

## Step-by-Step Workflow

The conversion process flows as follows:

### 1. Initiation (User Interface)

-   A user navigates to one of the conversion tabs in the Gradio UI (e.g., "✨(AI) SPF Conversion" or "✨(AI) DDL Conversion").
-   They either paste their Oracle code into a textbox or upload a `.sql` file.
-   Clicking the "Convert" button triggers a callback function in `ui/gradio_callbacks.py`.

**Key Files:**
-   `app.py`: Defines the Gradio UI components.
-   `ui/gradio_callbacks.py`: Contains the functions that handle UI events.

### 2. API Request and Job Creation

-   The Gradio callback function uses the `ui/api_client.py` to send a POST request to the backend's `/api/convert` endpoint.
-   The request payload includes the Oracle SQL code and the `job_type` (`spf` or `ddl`).
-   The backend API receives this request, creates a new job record in the database with a `pending` status, and immediately returns a unique `job_id` to the frontend.

**Key Files:**
-   `ui/api_client.py`: Helper to make requests to the backend.
-   `api/main.py`: The main FastAPI application.
-   `api/routes/conversion_routes.py`: Defines the `/convert` endpoint.
-   `api/database.py`: Contains functions to interact with the database (e.g., `create_job`).

### 3. Enqueuing the Job

-   After successfully creating the job in the database, the API endpoint publishes a message to the `conversion_jobs` queue in RabbitMQ.
-   This message is a JSON object containing the `job_id`, the `original_sql`, and the `job_type`.
-   This asynchronous step allows the API to respond quickly to the user while the time-consuming conversion happens in the background.

**Key Files:**
-   `api/queues.py`: Manages publishing messages to RabbitMQ.

### 4. Worker Processing

-   The `worker.py` process is continuously listening for new messages on the `conversion_jobs` queue.
-   When it picks up a new message, the `sql_conversion_callback` function is executed.
-   The worker first updates the job's status in the database to `processing`.

**Key Files:**
-   `worker.py`: The main file for the worker process, containing the `sql_conversion_callback`.

### 5. AI-Powered Conversion

-   The worker calls the core conversion logic located in `api/ai_converter.py`.
-   Based on the `job_type`, it calls either `convert_oracle_to_postgres` (for SPFs) or `convert_oracle_ddl_to_postgres_ddl` (for DDLs).
-   These functions are responsible for constructing a suitable prompt and sending the Oracle code to a Large Language Model (LLM) for translation.

**Key Files:**
-   `api/ai_converter.py`: The module that directly interfaces with the AI model for code conversion.

### 6. Verification

-   Once the AI model returns the translated PostgreSQL code, the worker proceeds to a verification step.
-   It calls the `verification.verify_procedure()` function, passing the newly converted code.
-   This function checks the syntactic validity of the generated SQL, potentially using libraries like `sqlparse` or by attempting to run it against a test database connection.

**Key Files:**
-   `api/verification.py`: Contains the logic to validate the output of the AI conversion.

### 7. Storing the Result

-   Based on the outcome of the verification step, the worker performs a final update on the job record in the database.
-   It sets the status to `verified` if successful or `failed` if issues are found.
-   The converted SQL code and any error messages from the verification step are saved to the job record. If a critical error occurred during any step, the status is set to `failed`.

**Key Files:**
-   `worker.py`
-   `api/database.py`

### 8. Retrieving the Result (User Interface)

-   While the worker is processing the job, the Gradio frontend periodically polls a status endpoint (e.g., `/api/jobs/{job_id}/status`).
-   Once the polling mechanism detects a final status (`verified`, `failed`, etc.), it makes one last call to retrieve the complete job details, including the converted code or error message.
-   The result is then displayed in the appropriate output textbox in the UI, and any download buttons are made visible.

**Key Files:**
-   `ui/gradio_callbacks.py`: Contains the polling logic (`poll_job_status`).
-   `api/routes/job_routes.py`: Defines the endpoints for checking job status and retrieving job results.
