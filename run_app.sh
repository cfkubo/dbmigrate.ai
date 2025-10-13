#!/bin/bash

# --- Open Web Interfaces ---

# Give services some time to start before opening browsers
# sleep 5

# open http://localhost:15672/#/ # RabbitMQ Management UI
# open http://localhost:3000/   # Grafana Dashboard
# open http://localhost:9090/query # Prometheus UI
# open http://localhost:7860/   # Gradio Web UI
# open http://localhost:16686/search # Jaeger UI (OpenTelemetry Tracing)

# docker exec -it some-rabbit rabbitmqadmin -f tsv -q list queues name | tr -d '\r' | xargs -I {} rabbitmqadmin delete queue name={}
# sleep 10

# --- Helper Functions ---

# Function to clean up background processes and containers
cleanup() {
    echo "Stopping background processes and containers..."
    if [ ! -z "$api_pid" ]; then
        kill $api_pid
        echo "API server (PID: $api_pid) stopped."
    fi
    if [ ! -z "$app_pid" ]; then
        kill $app_pid
        echo "Gradio Web UI (PID: $app_pid) stopped."
    fi
    if [ ! -z "$verifier_pid" ]; then
        kill $verifier_pid
        echo "Verifier (PID: $verifier_pid) stopped."
    fi

    echo "Cleanup complete."
}

# Trap signals and call the cleanup function
trap cleanup INT TERM EXIT

# clean up last run files
rm -rf __pycache__
rm -rf api/__pycache__
rm -rf api/routers/__pycache__
rm -rf .venv
rm -rf converted-*
rm -rf successfull-*
rm -rf failed-*

# Check for required commands
check_command() {
    if ! command -v $1 &> /dev/null;
    then
        echo "$1 could not be found. Please install it first."
        exit 1
    fi
}

# 1. Check for Dependencies
echo "--- Checking for dependencies ---"
check_command uv

check_command docker

# 2. Set up Virtual Environment
echo -e "\n--- Setting up Python environment ---"
if [ ! -d ".venv" ]; then
    uv venv
fi
source .venv/bin/activate
uv pip install -r requirements.txt
uv pip install -r verifier/requirements.txt

# 3. Export Database Credentials
export POSTGRES_DB="postgres"
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="password"
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"

# New variables for the application itself
export APP_POSTGRES_DB="migration_jobs"
export APP_POSTGRES_USER="migration_jobs"
export APP_POSTGRES_PASSWORD="password"

# RAG Database variables
export RAG_POSTGRES_DB="migratedbai"
export RAG_POSTGRES_USER="migration_jobs"
export RAG_POSTGRES_PASSWORD="password"
export RAG_POSTGRES_HOST="localhost"
export RAG_POSTGRES_PORT="5432"

export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"

# Load .env file if it exists to override defaults
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    set -a
    source .env
    set +a
fi

# 4. Run the Application
echo "\n--- Starting the application ---"

# Run the API server in the background
echo "Starting the API server... (logs will be in this terminal)"
uvicorn api.main:app --reload 2>&1 &
api_pid=$!
sleep 3

# Run the Web UI in the background
echo "Starting the Gradio Web UI... (logs will be in this terminal)"
python app.py 2>&1 &
app_pid=$!

# Run the verifier in the background
echo "Starting the Verifier... (logs will be in this terminal)"
python verifier/main.py 2>&1 &
verifier_pid=$!

# Instruct user to start worker manually
echo "-------------------------------------------------------------------"
echo "IMPORTANT: Please open a NEW TERMINAL and run the worker manually:"
echo "cd $(pwd) && source .venv/bin/activate && python worker.py"
echo "-------------------------------------------------------------------"
sleep 5 # Give user time to read the message

# Wait for all background processes to finish
wait




