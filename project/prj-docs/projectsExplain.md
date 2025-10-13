# Project Analysis: AI powered SQL to PSQL Syntax Converter

![logo](assets/logo1.png)

**Last Updated:** Thursday, July 24, 2025

This document provides a detailed breakdown of the project plan, architecture, and potential improvements for the Ora2Pg SPF Converter.

## 1. Project Plan & Purpose

**Primary Goal:** The main objective of this project is to provide a tool that can convert stored procedures and functions from an Oracle SQL dialect to a PostgreSQL compatible dialect.

**Key Features:**
1.  **Web UI:** A user-friendly web interface for converting SQL code by pasting it into a text box or uploading a file. It supports both Stored Procedures/Functions and DDL.
2.  **Web API:** Provides a web-accessible endpoint to perform conversions, allowing integration with other applications or web frontends. It has separate endpoints for Stored Procedures/Functions and DDL.
3.  **Asynchronous Conversion:** The conversion process is handled asynchronously, so users don't have to wait for the conversion to complete.
4.  **Verification and Self-Correction:** The converted SQL is verified against a PostgreSQL database, and if it fails, the tool attempts to self-correct the SQL using the LLM.

**Target User:** Database administrators and developers who are migrating a database from Oracle to PostgreSQL.

## 2. Architecture Diagram

The project follows a modular, message-driven architecture that separates the API, background workers, and the core logic.

![arch](assets/arch.png)

```
+---------------------+      +---------------------+
|    User (CLI)       |      |  User (API Client)  |
+-----------+---------+      +-----------+---------+
            |                          |
            |                          | HTTP Request (SQL String)
            v                          v
./gini.sh --[runs]--> +----------------------------+
            |         |       api/main.py          |
            v         | (Web Server/ASGI & Producer)|
+---------------------+ +----------------------------+
|     app.py          |             |
| (CLI Interface)     |             | 3. Creates/updates job status
+-----------+---------+             v
            |             +----------------------------+
            |             |   jobs.db (SQLite)         |
            |             | (Persistent Job Tracking)  |
            |             +-------------+--------------+
            |                           |
            +------------>--------------+  (Also via api/main.py)
            |                           |
            |                           v
            |             +----------------------------+
            |             |        RabbitMQ            |
            |             |   (Message Broker)         |
            +-----------> +-------------+--------------+
                          |             |
           2. Publishes jobs from api/main.py & app.py |
                          |             | 4. Consumes jobs from
                          |             v
                          +----------------------------+
                          |        Workers             |
                          | (Multiple worker.py instances)|
                          +-----------+----------------+
                                      |
                                      | 5. Converts SQL using
                                      v
                          +----------------------------+
                          |         Ollama LLM         |
                          |     (External Service)     |
                          +-----------+----------------+
                                      |
                                      | 6. Verifies SQL against
                                      v
                          +----------------------------+
                          |     PostgreSQL (Output)    |
                          |   (for Verification)       |
                          +-----------+----------------+
                                      |
                                      | 7. Publishes results back to
                                      v
                          +----------------------------+
                          |        RabbitMQ            |
                          |   (Message Broker)         |
                          +-----------+----------------+
                                      |
         8. Consumes results from (Result Collector)  |
                                      v
                          +----------------------------+
                          |    Result Collector        |
                          | (Async Result Consumer)    |
                          +-----------+----------------+
                                      |
                                      | 9. Updates final status in
                                      v
                          +----------------------------+
                          |   jobs.db (SQLite)         |
                          | (Persistent Job Tracking)  |
                          +----------------------------+
```


> Tip: If GitHub still fails to render the diagram, paste the block into https://mermaid.live to get a detailed parse error and line number. Keep node IDs simple (no spaces) and use quoted labels as shown above.

## 3. Component Breakdown

*   **`app.py`**: The entry point for the Gradio web application. It provides a UI with separate tabs for users to submit Stored Procedures/Functions and DDLs for conversion, either as text or file uploads.
*   **`gini.sh`**: A convenience shell script for setting up the environment and running the application.
*   **`api/`**: A Python package containing the web API and the core project logic.
    *   **`api/main.py`**: Sets up and runs the FastAPI web server. It receives conversion requests for both Stored Procedures/Functions and DDLs, creates jobs in the database, and provides an endpoint to check job status. It has endpoints like `/convert`, `/convert-file`, `/convert-ddl`, and `/convert-ddl-file`.
    *   **`api/logic.py`**: The brain of the project, containing the SQL dialect translation logic. It communicates with the Ollama LLM to perform the conversion.
    *   **`api/models.py`**: Defines the data structures for the API.
    *   **`api/database.py`**: Manages the SQLite database, including creating the jobs table and handling job creation, retrieval, and updates.
*   **`verifier/`**: A separate process that handles the conversion and verification of SQL.
    *   **`verifier/main.py`**: This is a background worker that polls the database for pending jobs, performs the conversion using `api/logic.py`, verifies the converted SQL against a PostgreSQL database, and attempts to self-correct any errors.
    *   **`verifier/requirements.txt`**: Lists the Python dependencies for the verifier process.
*   **`requirements.txt`**: Lists all the Python libraries the main project depends on.
*   **`sample.sql`**: An example Oracle SQL file for testing.

## 4. Asynchronous Job-Based Architecture

The application uses a job-based architecture to handle conversions asynchronously. This is a good design choice because the conversion process can be time-consuming. The same architecture is used for both Stored Procedure/Function and DDL conversions.

The workflow is as follows:
1.  The user submits a conversion request via the Gradio UI or the API.
2.  The FastAPI server creates a new job in the `jobs.db` SQLite database with a "pending" status and returns a job ID to the user.
3.  The `verifier/main.py` process, running in the background, polls the database for pending jobs.
4.  When it finds a pending job, the verifier converts the SQL using the Ollama LLM.
5.  The verifier then connects to a PostgreSQL database to check if the converted SQL is valid.
6.  If the SQL is valid, the job status is updated to "verified".
7.  If the SQL is invalid, the verifier sends the SQL and the error message back to the LLM to attempt a self-correction.
8.  If the self-correction is successful, the job status is updated to "verified".
9.  If the self-correction fails, the job status is updated to "failed".
10. The user can check the status of the job at any time by querying the `/job/{job_id}` endpoint.

## 5. Pros and Cons

**Pros:**
*   **Good Separation of Concerns:** The UI, API, and conversion logic are well-separated, making the code easier to maintain and test.
*   **Asynchronous by Design:** The job-based architecture is a good choice for a potentially long-running task like this.
*   **Verification and Self-Correction:** The verification and self-correction steps are a great feature that improves the reliability of the conversion.
*   **Clear Structure:** The project layout is logical and easy to understand.

**Cons:**
*   **Scalability of Logic:** The conversion logic is dependent on the capabilities of the LLM, which may not always produce correct or optimal SQL.
*   **No Visible Tests:** The lack of a `tests/` directory is a major risk, making it impossible to verify accuracy or prevent regressions.
*   **SQLite for Production:** While SQLite is fine for development, it's not recommended for production use, especially if the application needs to handle a high volume of requests.

## 6. Potential Improvements

### 1. Implement a Robust SQL Parsing Engine

While the LLM-based approach is flexible, a dedicated SQL parsing engine could provide more reliable and accurate conversions for common patterns. This could be used in combination with the LLM, where the parser handles the straightforward conversions and the LLM is used for the more complex cases.

### 2. Implement a Robust Testing Framework

*   Create a `tests/` directory.
*   Use `pytest` to write unit tests for the API and the conversion logic.
*   Create a wide variety of `sample_*.sql` files with different Oracle syntax and assert that the output is correct.

### 3. Use a More Robust Database

*   For production use, consider replacing SQLite with a more robust database like PostgreSQL. This would require changes in `api/database.py` and `verifier/main.py`.

### 4. Add Configuration Management

*   Introduce a `config.py` file or support for `.env` files to manage settings, such as database connection details and the Ollama model name.

### 5. Enhance Error Reporting

*   When the converter encounters syntax it cannot handle, it should provide more detailed error information to the user, including the line number and the specific error.

### 6. Containerize the Application

*   Add a `Dockerfile` to package the API and the verifier. This makes deployment trivial and ensures the environment is consistent.

## 7. Scalability and Resilience with RabbitMQ

To handle bulk operations and improve the overall robustness of the system, the project has been updated to integrate RabbitMQ as a message broker, shifting from a database-polling mechanism to a true producer/consumer architecture.

### New Architecture Flow

1.  **Producer (API):** When a user uploads a large SQL file, the `api/main.py` service acts as a producer. It splits the file into individual, convertible units (e.g., one function per unit) and publishes each unit as a persistent message to a `sql_conversion_requests` queue in RabbitMQ.

2.  **Message Broker (RabbitMQ):** RabbitMQ manages the flow of jobs. We use durable **Quorum Queues** to ensure that even if the server restarts, the conversion jobs are not lost.

3.  **Consumer (Worker):** A new, standalone `worker.py` process acts as the consumer. It listens for messages on the `sql_conversion_requests` queue. When it receives a job, it executes the time-consuming LLM conversion.

4.  **Result Handling:** Once a conversion is complete, the worker publishes the result to a `sql_conversion_results` queue. A separate process can then consume these results to assemble the final output or update the database.

### Key Improvements

This new architecture provides significant advantages:

*   **Massive Scalability:** The conversion workload is now distributed across one or more worker processes. To handle more jobs, you can simply run more `worker.py` instances. This allows for true parallel processing, dramatically increasing the throughput for bulk conversions.

*   **Decoupling and Performance:** The API is no longer directly tied to the conversion process. It can accept thousands of jobs in seconds and return an immediate confirmation to the user, as its only role is to publish messages. This makes the user-facing API extremely fast and responsive.

*   **Enhanced Resilience (Dead Letter Queue):** The system is now resilient to conversion failures. If a worker fails to process a message multiple times (a "poison message"), the message is automatically moved to a **Dead Letter Queue (DLQ)** after a configured number of retries. This prevents a single failing job from halting the entire conversion pipeline and allows developers to inspect failed jobs later for debugging.

*   **Improved Reliability:** By using RabbitMQ with persistent messaging and quorum queues, we ensure that jobs are safely stored and will be processed even in the event of worker or application crashes.
