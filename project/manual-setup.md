# Manual Setup and Running Instructions for SPF Converter

This guide provides step-by-step instructions to set up and run the SPF Converter application manually. This is useful for debugging and ensuring all components are running as expected.

## 1. Prerequisites

Before you begin, ensure you have the following installed on your system:
*   **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
*   **pip**: Python's package installer (usually comes with Python).
*   **venv**: Python's built-in module for creating virtual environments.
*   **Docker / Docker Compose**: If you are running RabbitMQ, Oracle, and PostgreSQL via Docker containers.

## 2. Navigate to the Project Directory

Open your terminal or command prompt and navigate to the root directory of the `spf-converter` project:

```bash
cd /Users/avannala/Documents/workspace/spf-converter
```

## 3. Create and Activate a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
```
(On Windows, use `.venv\Scripts\activate` instead of `source .venv/bin/activate`)

## 4. Install Dependencies

Install all required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

## 5. Set Up Environment Variables

The application relies on environment variables for configuration (e.g., database credentials, RabbitMQ host).

1.  Create a file named `.env` in the root directory of your project.
2.  Copy the contents of `.env.example` into your new `.env` file.
3.  Adjust the values in `.env` as per your local setup. Ensure that `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `RABBITMQ_HOST`, and `VERIFICATION_DB_*` settings are correct and consistent.

Example `.env` content (ensure this matches your actual setup):
```
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=migration_jobs
POSTGRES_USER=migration_jobs
POSTGRES_PASSWORD=password

# Oracle Configuration
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_USER=migrator
ORACLE_PASSWORD=password
ORACLE_SERVICE_NAME=xe
ORACLE_SID=xe

# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_URL=amqp://guest:guest@localhost:5672/%2F

# Redis Configuration
REDIS_HOST=192.168.106.2
REDIS_PORT=6379

VERIFICATION_DB_NAME=verification_db
VERIFICATION_DB_USER=migration_jobs
VERIFICATION_DB_PASSWORD=password
VERIFICATION_DB_HOST=localhost
VERIFICATION_DB_PORT=5432
```

## 6. Start Dependent Services (RabbitMQ, Oracle, PostgreSQL)

Ensure your RabbitMQ, Oracle, and PostgreSQL database instances are running and accessible. If you are using Docker Compose, you might start them like this:

```bash
docker-compose up -d rabbitmq postgres oracle # Adjust service names as per your docker-compose.yml
```

## 7. Start the API Server (`app.py`)

Open a new terminal window, activate your virtual environment (Step 3), and then start the FastAPI application:

```bash
source .venv/bin/activate
python app.py
```
This will start the API server, typically on `http://127.0.0.1:8000`.

## 8. Start the Worker (`worker.py`)

Open *another* new terminal window, activate your virtual environment (Step 3), and then start the worker process:

```bash
source .venv/bin/activate
python worker.py
```
The worker will connect to RabbitMQ and start processing jobs.

## 9. Test the SQL Execution Feature

Once both the API server and the worker are running, you can interact with the API (e.g., via a web UI, `curl`, or `Postman`) to submit a SQL execution job.

When you submit a SQL execution job, observe the logs in both the API server terminal and the worker terminal. The `print` statements we added should now be visible in the API server's logs if the relevant functions are being called.
