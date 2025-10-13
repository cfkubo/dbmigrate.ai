#!/bin/bash

# --- Configuration ---
DB_CONTAINER_NAME="ora2pg-postgres"
POSTGRES_DB="postgres"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="postgres"
POSTGRES_PORT="5432"
DOCKER_NETWORK="gini-network"

## Clean up stale files from previous runs
echo "--- Cleaning up stale files from previous runs ---"
# ----------------------
rm -rf converted-*
rm -rf failed-*
rm -rf jobs.db
rm -rf successful-*
rm -rf temp_*
rm -rf __pycache__
rm -rf api/__pycache__
# ----------------------

## clean up docker containers
# echo "--- Cleaning up existing Docker containers ---"
# docker rm -f $(docker ps -a -q) 2>/dev/null || true

# --- Helper Functions ---

# Check for required commands
check_command() {
    if ! command -v $1 &> /dev/null;
    then
        echo "$1 could not be found. Please install it first."
        exit 1
    fi
}

# Function to clean up background processes
cleanup() {
    echo "Stopping background processes..."
    if [ ! -z "$api_pid" ]; then
        kill $api_pid
    fi
}

# --- Main Script ---

# Trap Ctrl+C and call the cleanup function
trap cleanup INT EXIT

# 1. Check for Dependencies
echo "--- Checking for dependencies ---"
check_command uv
check_command docker
check_command ollama

# 2. Create Docker Network
echo -e "\n--- Creating Docker network ---"
docker network create ${DOCKER_NETWORK} || echo "Network '${DOCKER_NETWORK}' already exists."

# Kill any process running on port 8000 (sometime the process pile up and need to be cleaned up. - need to debug)
# echo "\n--- Checking for processes on port 8000 ---"
# echo "Processes running on port 8000 (if any):"
# sudo lsof -i :8000
# echo "Killing processes on port 8000..."
# sudo kill -9 $(sudo lsof -t -i:8000) && echo "Killed processes on port 8000." || echo "No processes found on port 8000."
# echo "Verifying no processes are running on port 8000:"
# sudo lsof -i :8000
# echo "---"

## Double check if ollama model is running
models=$(ps -ef | grep '[o]llama run' | grep -v "grep" | awk '{print $NF}' | sort -u)

# Check if any models were found.
if [ -z "$models" ]; then
  echo "No Ollama models currently running."
  exit 0
fi

echo "Found running models: "
echo "$models"
echo "---"

# # Loop through each unique model name and send a curl request.
# for model in $models
# do
#   echo "Querying model: $model"
#   # The curl command queries the local Ollama API for a simple joke.
#   # The model name is safely enclosed in single quotes inside the JSON string.
#   curl http://localhost:11434/api/generate -d '{
#     "model": "'"$model"'",
#     "prompt": "Tell me a joke",
#     "stream": false
#   }'
#   echo -e "\n---"
# done

# if [ $? -ne 0 ]; then
#     echo "Ollama model 'gpt-oss:latest' is not responding. Please ensure Ollama is running and the model is available."
#     exit 1
# fi

# 3. Set up Virtual Environment
echo -e "\n--- Setting up Python environment ---"
if [ ! -d ".venv" ]; then
    uv venv
fi
source .venv/bin/activate
uv pip install -r requirements.txt
uv pip install -r verifier/requirements.txt

# 4. Check if Ollama is running
echo -e "\n--- Checking Ollama status ---"
if ! ollama ps &> /dev/null;
then
    echo "Ollama is not running. Please start the Ollama application and try again."
    exit 1
fi
echo "Ollama is running."

# 5. Start RabbitMQ Container
echo -e "\n--- Setting up RabbitMQ ---"
if [ "$(docker ps -q -f name=some-rabbit)" ]; then
    echo "RabbitMQ container is already running."
elif [ "$(docker ps -aq -f status=exited -f name=some-rabbit)" ]; then
    echo "Starting existing RabbitMQ container..."
    docker start some-rabbit
else
    echo "Starting new RabbitMQ container..."
    docker run -d --hostname my-rabbit --name some-rabbit --network ${DOCKER_NETWORK} -p 5672:5672 -p 15672:15672 -p 15692:15692 rabbitmq:3-management
fi
sleep 5 # Give rabbitmq some time to start
echo "Enabling RabbitMQ Prometheus plugin..."
docker exec some-rabbit rabbitmq-plugins enable rabbitmq_prometheus

# 6. Start Monitoring Tools
echo -e "\n--- Setting up Monitoring (Prometheus & Grafana) ---"
if [ ! "$(docker ps -q -f name=prometheus)" ]; then
    echo "Starting new Prometheus container..."
    docker run -d \
      --name=prometheus \
      --network ${DOCKER_NETWORK} \
      -p 9090:9090 \
      prom/prometheus
else
    echo "Prometheus container is already running."
fi

if [ ! "$(docker ps -q -f name=grafana)" ]; then
    echo "Starting new Grafana container..."
    docker run -d \
      --name=grafana \
      --network ${DOCKER_NETWORK} \
      -p 3000:3000 -e GF_SECURITY_ADMIN_PASSWORD="password"  \
      grafana/grafana
else
    echo "Grafana container is already running."
fi

# 7. Start Oracle Container
echo -e "\n--- Setting up Oracle database ---"
if [ ! "$(docker ps -q -f name=^/oracle-free$)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=^/oracle-free$)" ]; then
        echo "Restarting existing Oracle container..."
        docker start oracle-free
    else
        echo "Starting a new Oracle container..."
        docker run -d --name=oracle-free --network ${DOCKER_NETWORK} -p 1521:1521 -e ORACLE_PASSWORD=password -v oracle-volume:/opt/oracle/oradata gvenzl/oracle-xe
    fi
    echo "Waiting for Oracle to be ready..."
    sleep 60 # It takes a while for Oracle to be ready
    echo "Configuring Oracle database..."
#     docker exec -i oracle-free sqlplus -s system/password <<EOF
# ALTER SESSION SET CONTAINER = CDB$ROOT;
# CREATE USER C##arul IDENTIFIED BY password CONTAINER=ALL;
# GRANT DBA TO C##arul CONTAINER=ALL;
# exit;
# EOF
else
    echo "Oracle container is already running."
fi

# 8. Start PostgreSQL Container
echo -e "\n--- Setting up PostgreSQL database ---"
if [ ! "$(docker ps -q -f name=^/${DB_CONTAINER_NAME}$)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=^/${DB_CONTAINER_NAME}$)" ]; then
        echo "Restarting existing PostgreSQL container..."
        docker start ${DB_CONTAINER_NAME}
    else
        echo "Starting a new PostgreSQL container..."
        docker run -d --name ${DB_CONTAINER_NAME} \
            --network ${DOCKER_NETWORK} \
            -e POSTGRES_DB=${POSTGRES_DB} \
            -e POSTGRES_USER=${POSTGRES_USER} \
            -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
            -p ${POSTGRES_PORT}:5432 \
            ankane/pgvector:latest
    fi
    echo "Waiting for PostgreSQL to be ready..."
    sleep 10
else
    echo "PostgreSQL container is already running."
fi

# 9. Export Database Credentials
# export POSTGRES_DB=${POSTGRES_DB}
# export POSTGRES_USER=${POSTGRES_USER}
# export POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
# export POSTGRES_HOST="localhost"
# export POSTGRES_PORT=${POSTGRES_PORT}

# 10. Run the Application
echo -e "\n--- Starting the application ---"

# Run the API server in the background
echo "Starting the API server... (logs will be in this terminal)"
uvicorn api.main:app --reload &
api_pid=$!
sleep 3


# Instruct user to start worker manually
echo "-------------------------------------------------------------------"
echo "IMPORTANT: Please open a NEW TERMINAL and run the worker manually:"
echo "cd $(pwd) && source .venv/bin/activate && python worker.py"
echo "-------------------------------------------------------------------"
sleep 5 # Give user time to read the message


# Run the Web UI in the foreground
echo "Starting the Gradio Web UI... (logs will be in this terminal)"
python app.py