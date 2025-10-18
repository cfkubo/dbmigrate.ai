#!/bin/bash

# --- Load Environment Variables ---
# Load variables from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# --- Helper Functions ---

# Check for required commands
check_command() {
    if ! command -v $1 &> /dev/null;
    then
        echo "$1 could not be found. Please install it first."
        exit 1
    fi
}

# --- Main Script ---

# 1. Check for Dependencies
echo "--- Checking for dependencies ---"
check_command docker

# 2. Create Docker Network
echo -e "\n--- Creating Docker network ---"
docker network create ${DOCKER_NETWORK} || echo "Network '${DOCKER_NETWORK}' already exists."

# 3. Start RabbitMQ Container
echo -e "\n--- Setting up RabbitMQ ---"
if [ "$(docker ps -q -f name=some-rabbit)" ]; then
    echo "RabbitMQ container is already running."
elif [ "$(docker ps -aq -f status=exited -f name=some-rabbit)" ]; then
    echo "Starting existing RabbitMQ container..."
    docker start some-rabbit
else
    echo "Starting new RabbitMQ container..."
    docker run -d --hostname my-rabbit --name some-rabbit \
    --network ${DOCKER_NETWORK} \
    -p 5672:5672 -p 15672:15672 -p 15692:15692 \
    rabbitmq:3-management
fi
sleep 5 # Give rabbitmq some time to start
echo "Enabling RabbitMQ Prometheus plugin..."
docker exec some-rabbit rabbitmq-plugins enable rabbitmq_prometheus

# 4. Start Monitoring Tools
echo -e "\n--- Setting up Monitoring (Prometheus & Grafana) ---"
if [ "$(docker ps -q -f name=prometheus)" ]; then
    echo "Prometheus container is already running."
elif [ "$(docker ps -aq -f status=exited -f name=prometheus)" ]; then
    echo "Starting existing Prometheus container..."
    docker start prometheus
else
    echo "Starting new Prometheus container..."
    docker run -d \
      --name=prometheus \
      --network ${DOCKER_NETWORK} \
      -p 9090:9090 \
      -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
      prom/prometheus
fi

if [ "$(docker ps -q -f name=grafana)" ]; then
    echo "Grafana container is already running."
elif [ "$(docker ps -aq -f status=exited -f name=grafana)" ]; then
    echo "Starting existing Grafana container..."
    docker start grafana
else
    echo "Starting new Grafana container..."
    docker run -d \
      --name=grafana \
      --network ${DOCKER_NETWORK} \
      -p 3000:3000 \
      -e GF_SECURITY_ADMIN_USER="admin" \
      -e GF_SECURITY_ADMIN_PASSWORD="password"  \
      -v $(pwd)/grafana/provisioning/datasources:/etc/grafana/provisioning/datasources \
      -v $(pwd)/grafana/provisioning/dashboards:/etc/grafana/provisioning/dashboards \
      -v $(pwd)/grafana/dashboards:/var/lib/grafana/dashboards \
      grafana/grafana
fi



# 5. Start Oracle Container
echo -e "\n--- Setting up Oracle database ---"
if [ ! "$(docker ps -q -f name=^/oracle-free$)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=^/oracle-free$)" ]; then
        echo "Restarting existing Oracle container..."
        docker start oracle-free
    else
        echo "Starting a new Oracle container..."
        docker run -d --name=oracle-free \
        --network ${DOCKER_NETWORK} \
        -p 1521:1521 \
        -e ORACLE_PASSWORD=password \
        -v /Users/projectsuno/Documents/workspace/spf-converter/sql-assets/customer_orders:/scripts \
        -v oracle-volume:/opt/oracle/oradata \
        my-custom-oracle-db:latest
        #gvenzl/oracle-xe
    fi
    echo "Waiting for Oracle to be ready..."
    sleep 60 # It takes a while for Oracle to be ready
    echo "Configuring Oracle database..."
   # docker exec -it oracle-free sqlplus sys/password as sysdba
else
    echo "Oracle container is already running."
fi

# 6. Start PostgreSQL Container
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

# 7. Start Valkey Container
echo -e "\n--- Setting up Valkey ---"
if [ "$(docker ps -q -f name=valkey)" ]; then
    echo "Valkey container is already running."
elif [ "$(docker ps -aq -f status=exited -f name=valkey)" ]; then
    echo "Starting existing Valkey container..."
    docker start valkey
else
    echo "Starting new Valkey container..."
    docker run -d --name valkey --network ${DOCKER_NETWORK} -p 6379:6379 valkey/valkey:latest
fi
sleep 5 # Give Valkey some time to start

# 8. Start MySQL Container
echo -e "\n--- Setting up MySQL ---"
if [ "$(docker ps -q -f name=mysql)" ]; then
    echo "MySQL container is already running."
elif [ "$(docker ps -aq -f status=exited -f name=mysql)" ]; then
    echo "Starting existing MySQL container..."
    docker start mysql
else
    echo "Starting new MySQL container..."
    docker run -d --name mysql \
        --network ${DOCKER_NETWORK} \
        -e MYSQL_ROOT_PASSWORD=password \
        -e MYSQL_DATABASE=mysql \
        -e MYSQL_USER=root \
        -e MYSQL_PASSWORD=password \
        -p 3306:3306 \
        mysql:8.0
fi
sleep 15 # Give MySQL some time to start

# 9. Start SQL Server Container
echo -e "\n--- Setting up SQL Server ---"
if [ "$(docker ps -q -f name=sqlserver)" ]; then
    echo "SQL Server container is already running."
elif [ "$(docker ps -aq -f status=exited -f name=sqlserver)" ]; then
    echo "Starting existing SQL Server container..."
    docker start sqlserver
else
    echo "Starting new SQL Server container..."
    docker run -d --name sqlserver \
        --network ${DOCKER_NETWORK} \
        -e ACCEPT_EULA=Y \
        -e SA_PASSWORD=password \
        -p 1433:1433 \
        mcr.microsoft.com/mssql/server:2019-latest
fi
sleep 15 # Give SQL Server some time to start

# 10. Start DB2 Container
echo -e "\n--- Setting up DB2 ---"
if [ "$(docker ps -q -f name=db2)" ]; then
    echo "DB2 container is already running."
elif [ "$(docker ps -aq -f status=exited -f name=db2)" ]; then
    echo "Starting existing DB2 container..."
    docker start db2
else
    echo "Starting new DB2 container..."
    docker run -d --name db2 \
        --network ${DOCKER_NETWORK} \
        -e ACCEPT_LICENSE=yes \
        -e DB2INSTANCE=db2inst1 \
        -e DB2INST1_PASSWORD=password \
        -e DBNAME=BLUDB \
        -p 50000:50000 \
        ibmcom/db2:latest
fi
sleep 60 # Give DB2 some time to start

# 11. Start Teradata Container (Placeholder)
# echo -e "\n--- Setting up Teradata ---"
# echo "NOTE: There is no official public Docker image for Teradata."
# echo "You must have a local or private image to run this container."
# if [ "$(docker ps -q -f name=teradata)" ]; then
#     echo "Teradata container is already running."
# elif [ "$(docker ps -aq -f status=exited -f name=teradata)" ]; then
#     echo "Starting existing Teradata container..."
#     docker start teradata
# else
#     echo "Starting new Teradata container... (This will fail without a valid image)"
#     # docker run -d --name teradata \
#     #     --network ${DOCKER_NETWORK} \
#     #     -e TERADATA_USER=dbc \
#     #     -e TERADATA_PASSWORD=dbc \
#     #     -p 1025:1025 \
#     #     your-private-teradata-image:latest
# fi
# sleep 60 # Give Teradata some time to start

# 12. Start OpenTelemetry Collector Container
echo -e "\n--- Setting up OpenTelemetry Collector for Tracing ---"
if [ "$(docker ps -q -f name=otel-collector)" ]; then
    echo "OpenTelemetry Collector container is already running."
elif [ "$(docker ps -aq -f status=exited -f name=otel-collector)" ]; then
    echo "Starting existing OpenTelemetry Collector container..."
    docker start otel-collector
else
    echo "Starting new OpenTelemetry Collector container..."
    docker pull otel/opentelemetry-collector-contrib:latest
    docker run -d --name otel-collector \
      --network ${DOCKER_NETWORK} \
      -p 4317:4317 \
      -p 4318:4318 \
      -v $(pwd)/otel-collector-config.yaml:/etc/otel-collector-config.yaml \
      otel/opentelemetry-collector-contrib:latest \
      --config /etc/otel-collector-config.yaml
fi
sleep 5 # Give OpenTelemetry Collector some time to start

# 11. Start Jaeger Container
echo -e "\n--- Setting up Jaeger for Tracing ---"
if [ "$(docker ps -q -f name=jaeger)" ]; then
    echo "Jaeger container is already running."
elif [ "$(docker ps -aq -f status=exited -f name=jaeger)" ]; then
    echo "Starting existing Jaeger container..."
    docker start jaeger
else
    echo "Starting new Jaeger container..."
    docker run -d --name jaeger \
      -e COLLECTOR_OTLP_ENABLED=true \
      -p 16686:16686 --network ${DOCKER_NETWORK} \
      jaegertracing/all-in-one:latest
fi
sleep 5 # Give Jaeger some time to start