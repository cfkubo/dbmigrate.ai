docker exec -it oracle-free sqlplus sys/password as sysdba

docker exec -it oracle-free sqlplus sys/password as sysdba


GRANT ALTER ANY SESSION TO SYSTEM;
GRANT DBA TO SYSTEM;


docker run -d  --name oracle-free -p 1521:1521 -e ORACLE_PWD=password container-registry.oracle.com/database/free:latest-lite

ALTER SESSION SET CONTAINER = CDB$ROOT;

CREATE USER C##arul IDENTIFIED BY password CONTAINER=ALL;
GRANT DBA TO C##arul CONTAINER=ALL;


SHOW PDBS;

ALTER SESSION SET CONTAINER = FREEPDB1;

CREATE USER DEMOARUL IDENTIFIED BY password;
GRANT DBA TO DEMOARUL;

GRANT CREATE SESSION, UNLIMITED TABLESPACE TO DEMOARUL;




ALTER SESSION SET CONTAINER = CDB$ROOT;

CREATE USER C##demo IDENTIFIED BY password CONTAINER=ALL;
GRANT DBA TO C##demo CONTAINER=ALL;


docker exec -it some-rabbit rabbitmqadmin -f tsv -q list queues name | tr -d '\r' | xargs -I {} rabbitmqadmin delete queue name={}

CREATE USER migration_jobs WITH PASSWORD 'password' SUPERUSER;


SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'migration_jobs';



docker run -d \
      --name=prometheus \
      -p 9090:9090 \
      prom/prometheus


docker run -d \
      --name=grafana \
      -p 3000:3000 -e GF_SECURITY_ADMIN_PASSWORD="password"  \
      grafana/grafana

podman run -d \
      --name=prometheus \
      -p 9090:9090 \
      prom/prometheus

podman run -d \
      --name=grafana \
      -p 3000:3000 \
      grafana/grafana



docker network create rmq-network

docker run -d --hostname my-rabbit --name rabbitmq --network rmq-network  -p 15672:15672 -p 15692:15692 -p 5552:5552 rabbitmq:4.0-management

docker run -d --hostname my-rabbit-green --name rabbitmq-green --network rmq-network  -p 15673:15672 -p 15691:15692 -p 5553:5552 rabbitmq:4.0-management
