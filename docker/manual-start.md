projectsuno@projects-MacBook-Pro spf-converter % docker run -d --hostname my-rabbit --name some-rabbit -p 5672:5672 -p 15672:15672 rabbitmq:3-management
dac957fece56103735331345658c561b6a0909e29d5e22d0602edbe3d5080792
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter % sh gini.sh
--- Checking for dependencies ---

--- Creating Docker network ---
"docker network create" requires exactly 1 argument.
See 'docker network create --help'.

Usage:  docker network create [OPTIONS] NETWORK

Create a network
Network '' already exists.

--- Setting up RabbitMQ ---
RabbitMQ container is already running.
Enabling RabbitMQ Prometheus plugin...
Enabling plugins on node rabbit@my-rabbit:
rabbitmq_prometheus
The following plugins have been configured:
  rabbitmq_federation
  rabbitmq_management
  rabbitmq_management_agent
  rabbitmq_prometheus
  rabbitmq_web_dispatch
Applying plugin configuration to rabbit@my-rabbit...
Plugin configuration unchanged.

--- Setting up Monitoring (Prometheus & Grafana) ---
Starting new Prometheus container...
Unable to find image '9090:9090' locally
docker: Error response from daemon: pull access denied for 9090, repository does not exist or may require 'docker login': denied: requested access to the resource is denied.
See 'docker run --help'.
Starting new Grafana container...
Unable to find image '3000:3000' locally
docker: Error response from daemon: pull access denied for 3000, repository does not exist or may require 'docker login': denied: requested access to the resource is denied.
See 'docker run --help'.

--- Setting up Oracle database ---
Starting a new Oracle container...
Unable to find image '1521:1521' locally
docker: Error response from daemon: pull access denied for 1521, repository does not exist or may require 'docker login': denied: requested access to the resource is denied.
See 'docker run --help'.
Waiting for Oracle to be ready...
^C
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter % source .env
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter % docker rm some-rabbit
Error response from daemon: cannot remove container "/some-rabbit": container is running: stop the container before removing or force remove
projectsuno@projects-MacBook-Pro spf-converter % docker stop some-rabbit
some-rabbit
projectsuno@projects-MacBook-Pro spf-converter % docker rm some-rabbit
some-rabbit
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %     docker run -d --hostname my-rabbit --name some-rabbit --network ${DOCKER_NETWORK} -p 5672:5672 -p 15672:15672 -p 15692:15692 rabbitmq:3-management

75d0a0d97d9bf780fc200de6beea8c71666cd28dda7a1d7e54bf49df3c3c201d
projectsuno@projects-MacBook-Pro spf-converter % docker run -d \
      --name=prometheus \
      --network ${DOCKER_NETWORK} \
      -p 9090:9090 \
      -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
      prom/prometheus
5f8da9c4f8b9cbbcfac34f3d932d557055bf04f97080f127c10a5e4f07f65e82
projectsuno@projects-MacBook-Pro spf-converter % docker run -d \
      --name=grafana \
      --network ${DOCKER_NETWORK} \
      -p 3000:3000 \
       GF_SECURITY_ADMIN_USER="admin" \
       GF_SECURITY_ADMIN_PASSWORD="password"  \
      -v $(pwd)/grafana/provisioning/datasources:/etc/grafana/provisioning/datasources \
      -v $(pwd)/grafana/provisioning/dashboards:/etc/grafana/provisioning/dashboards \
      -v $(pwd)/grafana/dashboards:/var/lib/grafana/dashboards \
      grafana/grafana
docker: invalid reference format: repository name (library/GF_SECURITY_ADMIN_USER=admin) must be lowercase.
See 'docker run --help'.
projectsuno@projects-MacBook-Pro spf-converter % docker run -d \
      --name=grafana \
      --network ${DOCKER_NETWORK} \
      -p 3000:3000 \
      - GF_SECURITY_ADMIN_USER="admin" \
      - GF_SECURITY_ADMIN_PASSWORD="password"  \
      -v $(pwd)/grafana/provisioning/datasources:/etc/grafana/provisioning/datasources \
      -v $(pwd)/grafana/provisioning/dashboards:/etc/grafana/provisioning/dashboards \
      -v $(pwd)/grafana/dashboards:/var/lib/grafana/dashboards \
      grafana/grafana
docker: invalid reference format.
See 'docker run --help'.
projectsuno@projects-MacBook-Pro spf-converter % docker run -d \
      --name=grafana \
      --network ${DOCKER_NETWORK} \
      -p 3000:3000 \
      -v GF_SECURITY_ADMIN_USER="admin" \
      -v GF_SECURITY_ADMIN_PASSWORD="password"  \
      -v $(pwd)/grafana/provisioning/datasources:/etc/grafana/provisioning/datasources \
      -v $(pwd)/grafana/provisioning/dashboards:/etc/grafana/provisioning/dashboards \
      -v $(pwd)/grafana/dashboards:/var/lib/grafana/dashboards \
      grafana/grafana
8d2797443d21c8c06bf96991ea400666f7e339ff515c7776d7a3df618d38dbce
projectsuno@projects-MacBook-Pro spf-converter % docker run -d --name=oracle-free \
--network ${DOCKER_NETWORK} \
-p 1521:1521 \
 ORACLE_PASSWORD=password \
-v oracle-volume:/opt/oracle/oradata \
my-custom-oracle-db:latest
docker: invalid reference format: repository name (library/ORACLE_PASSWORD=password) must be lowercase.
See 'docker run --help'.
projectsuno@projects-MacBook-Pro spf-converter % docker run -d --name=oracle-free \
--network ${DOCKER_NETWORK} \
-p 1521:1521 \
-v ORACLE_PASSWORD=password \
-v oracle-volume:/opt/oracle/oradata \
my-custom-oracle-db:latest
ad7903c0530bcc25655d269d7c06a2618ce3df09a3d9e978644e000357e51560
projectsuno@projects-MacBook-Pro spf-converter % docker run -d --name ${DB_CONTAINER_NAME} \
            --network ${DOCKER_NETWORK} \
            -v POSTGRES_DB=${POSTGRES_DB} \
            -v POSTGRES_USER=${POSTGRES_USER} \
            -v  POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
            -p ${POSTGRES_PORT}:5432 \
            ankane/pgvector:latest
706233e7ecea8f01f34cd8ffb01f58fbcbff82777831de57d040329e4a1bd6ef
projectsuno@projects-MacBook-Pro spf-converter % docker run -d --name otel-collector \
      --network ${DOCKER_NETWORK} \
      -p 4317:4317 \
      -p 4318:4318 \
      -v $(pwd)/otel-collector-config.yaml:/etc/otel-collector-config.yaml \
      otel/opentelemetry-collector-contrib:latest \
      --config /etc/otel-collector-config.yaml
8943636fe7681a16674c43bd21b80268889855a603bc03b8033765e976f98cda
projectsuno@projects-MacBook-Pro spf-converter % docker run -d --name jaeger \
       COLLECTOR_OTLP_ENABLED=true \
      -p 16686:16686 --network ${DOCKER_NETWORK} \
      jaegertracing/all-in-one:latest
docker: invalid reference format: repository name (library/COLLECTOR_OTLP_ENABLED=true) must be lowercase.
See 'docker run --help'.
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter % docker run -d --name jaeger \
      -v COLLECTOR_OTLP_ENABLED=true \
      -p 16686:16686 --network ${DOCKER_NETWORK} \
      jaegertracing/all-in-one:latest
c9531b19aae7cae08de4bdd21c81494b4bda66b48a4674f4f25046235d7a2407
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter % docker ps -a
CONTAINER ID   IMAGE                                         COMMAND                  CREATED          STATUS                     PORTS                                                                                                                                                                                          NAMES
c9531b19aae7   jaegertracing/all-in-one:latest               "/go/bin/all-in-one-…"   42 seconds ago   Up 42 seconds              4317-4318/tcp, 9411/tcp, 14250/tcp, 14268/tcp, 0.0.0.0:16686->16686/tcp, :::16686->16686/tcp                                                                                                   jaeger
8943636fe768   otel/opentelemetry-collector-contrib:latest   "/otelcol-contrib --…"   2 minutes ago    Up 2 minutes               0.0.0.0:4317-4318->4317-4318/tcp, :::4317-4318->4317-4318/tcp, 55679/tcp                                                                                                                       otel-collector
706233e7ecea   ankane/pgvector:latest                        "docker-entrypoint.s…"   2 minutes ago    Exited (1) 2 minutes ago                                                                                                                                                                                                  ora2pg-postgres
ad7903c0530b   my-custom-oracle-db:latest                    "container-entrypoin…"   2 minutes ago    Up 2 minutes               0.0.0.0:1521->1521/tcp, :::1521->1521/tcp                                                                                                                                                      oracle-free
8d2797443d21   grafana/grafana                               "/run.sh"                3 minutes ago    Up 3 minutes               0.0.0.0:3000->3000/tcp, :::3000->3000/tcp                                                                                                                                                      grafana
5f8da9c4f8b9   prom/prometheus                               "/bin/prometheus --c…"   5 minutes ago    Up 5 minutes               0.0.0.0:9090->9090/tcp, :::9090->9090/tcp                                                                                                                                                      prometheus
75d0a0d97d9b   rabbitmq:3-management                         "docker-entrypoint.s…"   5 minutes ago    Up 5 minutes               4369/tcp, 5671/tcp, 0.0.0.0:5672->5672/tcp, :::5672->5672/tcp, 15671/tcp, 0.0.0.0:15672->15672/tcp, :::15672->15672/tcp, 15691/tcp, 25672/tcp, 0.0.0.0:15692->15692/tcp, :::15692->15692/tcp   some-rabbit
projectsuno@projects-MacBook-Pro spf-converter % docker logs 706233e7ecea
Error: Database is uninitialized and superuser password is not specified.
       You must specify POSTGRES_PASSWORD to a non-empty value for the
       superuser. For example, "-e POSTGRES_PASSWORD=password" on "docker run".

       You may also use "POSTGRES_HOST_AUTH_METHOD=trust" to allow all
       connections without a password. This is *not* recommended.

       See PostgreSQL documentation about "trust":
       https://www.postgresql.org/docs/current/auth-trust.html
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter % source .evn
source: no such file or directory: .evn
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter % source .env
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter % docker ora2pg-postgres
docker: 'ora2pg-postgres' is not a docker command.
See 'docker --help'
projectsuno@projects-MacBook-Pro spf-converter % docker rm ora2pg-postgres
ora2pg-postgres
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter % docker run -d --name ${DB_CONTAINER_NAME} \
            --network ${DOCKER_NETWORK} \
            -v POSTGRES_DB=${POSTGRES_DB} \
            -v POSTGRES_USER=${POSTGRES_USER} \
            -v  POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
            -p ${POSTGRES_PORT}:5432 \
            ankane/pgvector:latest
1d4268ffa92f63b6dc2f000504e82cd166fba06a631862b588c1fca458a03a30
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter % docker logs ora2pg-postgres
Error: Database is uninitialized and superuser password is not specified.
       You must specify POSTGRES_PASSWORD to a non-empty value for the
       superuser. For example, "-e POSTGRES_PASSWORD=password" on "docker run".

       You may also use "POSTGRES_HOST_AUTH_METHOD=trust" to allow all
       connections without a password. This is *not* recommended.

       See PostgreSQL documentation about "trust":
       https://www.postgresql.org/docs/current/auth-trust.html
projectsuno@projects-MacBook-Pro spf-converter % docker rm ora2pg-postgres
ora2pg-postgres
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter % docker run -d --name ${DB_CONTAINER_NAME} \
            --network ${DOCKER_NETWORK} \
            -v POSTGRES_DB=${POSTGRES_DB} \
            -v POSTGRES_USER=${POSTGRES_USER} \
            -v POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
            -p ${POSTGRES_PORT}:5432 \
            ankane/pgvector:latest
33bee33d1c31716850102d16ba1c147b142f6a471eae9e71086c5ebfaa198b6a
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter % docker logs ora2pg-postgres
Error: Database is uninitialized and superuser password is not specified.
       You must specify POSTGRES_PASSWORD to a non-empty value for the
       superuser. For example, "-e POSTGRES_PASSWORD=password" on "docker run".

       You may also use "POSTGRES_HOST_AUTH_METHOD=trust" to allow all
       connections without a password. This is *not* recommended.

       See PostgreSQL documentation about "trust":
       https://www.postgresql.org/docs/current/auth-trust.html
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter % docker run -d --name ${DB_CONTAINER_NAME} \
    --network ${DOCKER_NETWORK} \
    -e POSTGRES_DB=${POSTGRES_DB} \          # <-- CORRECT: Use -e for environment variables
    -e POSTGRES_USER=${POSTGRES_USER} \      # <-- CORRECT: Use -e for environment variables
    -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \ # <-- CORRECT: Use -e for environment variables
    -p ${POSTGRES_PORT}:5432 \
    ankane/pgvector:latest
zsh: bad pattern: #
zsh: bad pattern: #
zsh: no matches found:  #
zsh: command not found: -p
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter % docker run -d --name ${DB_CONTAINER_NAME} \
            --network ${DOCKER_NETWORK} \
            -e POSTGRES_DB=${POSTGRES_DB} \
            -e POSTGRES_USER=${POSTGRES_USER} \
            -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
            -p ${POSTGRES_PORT}:5432 \
            ankane/pgvector:latest
docker: Error response from daemon: Conflict. The container name "/ora2pg-postgres" is already in use by container "33bee33d1c31716850102d16ba1c147b142f6a471eae9e71086c5ebfaa198b6a". You have to remove (or rename) that container to be able to reuse that name.
See 'docker run --help'.
projectsuno@projects-MacBook-Pro spf-converter % docker rm ora2pg-postgres
ora2pg-postgres
projectsuno@projects-MacBook-Pro spf-converter %
projectsuno@projects-MacBook-Pro spf-converter % docker run -d --name ${DB_CONTAINER_NAME} \
            --network ${DOCKER_NETWORK} \
            -e POSTGRES_DB=${POSTGRES_DB} \
            -e POSTGRES_USER=${POSTGRES_USER} \
            -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
            -p ${POSTGRES_PORT}:5432 \
            ankane/pgvector:latest
0f130d029bea78cbb386cbaad123a841363c600709ac6b0b8687798606d117ab