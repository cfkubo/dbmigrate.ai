# dbmigrate.ai

## Overview

**dbmigrate.ai** is an AI-powered tool designed to facilitate the migration of databases from Oracle to PostgreSQL. It offers a comprehensive solution with a web-based user interface and a RESTful API to streamline the entire migration process.

The tool leverages a local Ollama Large Language Model (LLM) to automatically convert Oracle SQL syntax (including Stored Procedures, Functions, and Data Definition Languages - DDLs) to be compatible with PostgreSQL.

## Key Features

- **AI-Powered SQL Conversion:** Automatically converts Oracle SQL to PostgreSQL syntax.
- **Database Metadata Extraction:** Extracts schema information and DDLs from Oracle databases for various objects like Tables, Views, Procedures, etc.
- **SQL Execution:** Executes SQL scripts on the target PostgreSQL database.
- **Data Migration:** Migrates data from Oracle tables to their PostgreSQL counterparts.
- **Verification:** Verifies the converted SQL against the target PostgreSQL database to ensure compatibility and correctness.
- **Web UI:** An intuitive Gradio-based web interface for:
    - Database connection management (Oracle and PostgreSQL).
    - Metadata extraction from Oracle.
    - SQL conversion (from text input or file upload).
    - SQL script execution on PostgreSQL.
    - Data migration management.
    - Real-time job status monitoring.
- **REST API:** A FastAPI-based API that allows for programmatic control over all migration functionalities.
- **Asynchronous by Design:** Utilizes RabbitMQ as a message broker to handle time-consuming tasks like SQL conversion and data migration asynchronously, ensuring the UI remains responsive.
- **Job Tracking:** Employs a PostgreSQL database to persist and track the status of all migration jobs.
- **Containerized Environment:** Uses Docker to run all necessary services, including RabbitMQ, Oracle, and PostgreSQL, ensuring a consistent and reproducible environment.

## Project Structure

The project is organized into several key components:

- **`app.py`:** The entry point for the Gradio web UI.
- **`worker.py`:** The core worker process that listens for tasks on the RabbitMQ queue and performs the conversion, verification, and migration operations.
- **`api/`:** The backend application built with FastAPI.
    - **`main.py`:** Defines the API endpoints.
    - **`ai_converter.py`:** Handles the SQL conversion logic using the Ollama model.
    - **`database.py`:** Manages the connection and operations with the job tracking database.
    - **`migration_db.py`:** Contains the logic for data migration.
    - **`oracle_helper.py`:** A set of utility functions for interacting with Oracle databases.
    - **`postgres_utils.py`:** A set of utility functions for interacting with PostgreSQL databases.
    - **`queues.py`:** Manages the RabbitMQ message queues.
    - **`schema_comparer.py`:** Compares the schemas of the source and target databases.
    - **`verification.py`:** Handles the verification of the converted SQL.
- **`frontend/`:** Contains a React-based frontend.
- **`ui/`:** Includes the callbacks and API client for the Gradio UI.
- **`verifier/`:** Contains the logic for the database migration verification process.
- **`sql-assets/`:** A collection of sample SQL files for testing purposes.
- **`docker/`:** Contains Dockerfiles and other Docker-related configuration.
- **`gini.sh`:** A utility script to set up and run the entire application stack.

## Architecture

The application follows a distributed architecture:

1.  The **Web UI** or an **API Client** initiates a migration job.
2.  The **API Server** (FastAPI) receives the request, creates a job in the database, and publishes a message to a **RabbitMQ** queue.
3.  One or more **Workers** consume the message from the queue.
4.  The worker performs the required task (e.g., SQL conversion using the **Ollama LLM**, data migration).
5.  The worker updates the job status in the database.
6.  The **Web UI** polls the API server to get the latest job status and displays it to the user.
