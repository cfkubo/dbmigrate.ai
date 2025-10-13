# Building and Running the Application with Docker

This document provides instructions on how to build and run the application using Docker and Docker Compose.

## Prerequisites

*   Docker installed
*   Docker Compose installed

## Steps

1.  **Navigate to the docker directory:**

    ```bash
    cd docker
    ```

2.  **Build and run the services:**

    Use the following command to build the Docker images and start the containers for all the services defined in the `docker-compose.yml` file.

    ```bash
    docker-compose up --build
    ```

    This will start the following services:
    *   `rabbitmq`: Message broker
    *   `postgres`: Database
    *   `api`: Backend API
    *   `worker`: Background worker
    *   `ui`: User interface

    The services will be running in the same network and will be able to communicate with each other.

    You can access the services at the following ports:
    *   **RabbitMQ Management:** http://localhost:15672
    *   **PostgreSQL:** localhost:5432
    *   **API:** http://localhost:8000
    *   **UI:** http://localhost:7860

## Stopping the application

To stop the application, press `Ctrl+C` in the terminal where `docker-compose` is running, and then run the following command to remove the containers:

```bash
docker-compose down
```
