# Data Migration Feature Plan

This document outlines the architecture and implementation plan for adding a new data migration feature to the project. This feature will allow users to transfer data from an Oracle database to a PostgreSQL database through a user-friendly Gradio web interface.

## Proposed Architecture

The proposed architecture is designed to be robust, scalable, and user-friendly. It decouples the long-running data migration process from the web interface using a message queue (RabbitMQ). This prevents UI timeouts and provides a better user experience.

```
+-------------+       +------------------------+       +------------------+
|             |       |                        |       |                  |
|  Gradio UI  |------>|   Web Server (API)     |------>|    RabbitMQ      |
|  (`app.py`) |       |   (Gradio Functions)   |       |  (Message Broker)|
|             |       |                        |       |                  |
+-------------+       +------------------------+       +------------------+
      ^                                                        |
      |                                                        | (Consumes Task)
      | (Polls for Status)                                     |
      |                                                        v
+-----+-------------+       +------------------+       +------------------+
|  Status & Results |<------|                  |<----->|                  |
|  (e.g., Redis)    |       |   Worker Process |       |   Oracle DB      |
+-------------------+------>|     (`worker.py`)  |       |   (Source)       |
                            |                  |<----->|                  |
                            +------------------+       |   Postgres DB    |
                                                     |   (Destination)  |
                                                     +------------------+
```

### Architectural Flow

1.  **Gradio UI (`app.py`):** The user interacts with the Gradio interface to provide database credentials, select tables, and initiate the migration.
2.  **Web Server (Gradio Functions):** The Python functions backing the Gradio UI receive the request. Instead of performing the migration directly, they package the job details (credentials, table names) into a message and publish it to a RabbitMQ queue. An immediate `task_id` is generated and used to track the job.
3.  **RabbitMQ:** This message broker holds the migration task in a queue until a worker is available to process it.
4.  **Worker (`worker.py`):** A separate, continuously running Python process listens for tasks on the RabbitMQ queue. When it receives a task, it performs the heavy lifting: connects to both databases, reads data from Oracle in chunks, writes data to Postgres, and handles any errors.
5.  **Status Store (Redis):** As the worker makes progress, it posts status updates (e.g., "In Progress", "Copied 50% of rows", "Completed") to a Redis key-value store, using the `task_id` as the key.
6.  **Polling for Status:** The Gradio UI periodically calls a function that reads the status from Redis for its `task_id` and displays the latest progress to the user, creating a live-updating experience.

## Gradio UI Flow

The user experience within the Gradio app will be as follows:

1.  **Input Credentials:** The user will be presented with text fields to enter connection details for both Oracle and PostgreSQL (host, port, user, password, database/service name).
2.  **Connect & Fetch Tables:** A "Connect" button next to each database form will trigger a function that tests the connection and, upon success, dynamically populates a `gr.Dropdown` component with the list of tables from that database.
3.  **Select Tables:** The user selects the source Oracle table and the destination PostgreSQL table from the populated dropdowns.
4.  **Migrate:** A "Migrate Data" button triggers the main migration function, which sends the task to the RabbitMQ queue in the background and returns a task ID.
5.  **View Progress:** A status text box on the UI will automatically update every few seconds by polling a status-checking function, showing the user the real-time progress of the migration.

## Implementation Steps

1.  **Update Dependencies (`requirements.txt`):**
    *   Add `oracledb` for Oracle connectivity.
    *   Add `psycopg2-binary` for PostgreSQL connectivity.
    *   Add `pika` for RabbitMQ communication.
    *   Add `redis` for the status-sharing mechanism.
    *   Ensure `gradio` is present.

2.  **Update Docker (`docker-compose.yml`):**
    *   Add a `rabbitmq` service to the compose file.
    *   Add a `redis` service to the compose file.
    *   Ensure the application and worker services are configured to connect to them.

3.  **Modify `worker.py`:**
    *   Implement the core data migration logic.
    *   Set up the worker to listen to the RabbitMQ queue.
    *   On receiving a task, connect to the databases, transfer data in chunks, and update the status in Redis.

4.  **Build the UI in `app.py`:**
    *   Create a new `gr.Blocks` interface for the data migration feature.
    *   Define the Gradio components (text boxes, buttons, dropdowns, status labels).
    *   Implement the Python functions that power the UI:
        *   `update_oracle_tables(...)`: Connects to Oracle and returns an updated `gr.Dropdown` with table names.
        *   `update_postgres_tables(...)`: Does the same for PostgreSQL.
        *   `start_migration_task(...)`: Publishes the job to RabbitMQ and stores the initial status in Redis.
        *   `check_migration_status(...)`: Fetches the latest status from Redis, designed to be called in a loop by the Gradio UI.
