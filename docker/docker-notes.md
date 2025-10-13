projectsuno@projects-MacBook-Pro docker % docker build -t my-custom-oracle-db .
failed to fetch metadata: fork/exec /Users/projectsuno/.docker/cli-plugins/docker-buildx: no such file or directory

DEPRECATED: The legacy builder is deprecated and will be removed in a future release.
            Install the buildx component to build images with BuildKit:
            https://docs.docker.com/go/buildx/

Sending build context to Docker daemon   2.56kB
Step 1/3 : FROM gvenzl/oracle-free:latest
 ---> 23112ee46e73
Step 2/3 : ENV ORACLE_PASSWORD=your_secure_password
 ---> Using cache
 ---> 9fb034b35742
Step 3/3 : EXPOSE 1521
 ---> Running in bf2c937d77bc
 ---> Removed intermediate container bf2c937d77bc
 ---> a0bd7f212428
Successfully built a0bd7f212428
Successfully tagged my-custom-oracle-db:latest
projectsuno@projects-MacBook-Pro docker % docker run -d --name=oracle-free \
        --network ${DOCKER_NETWORK} \
        -p 1521:1521 \
        -e ORACLE_PASSWORD=password \
        -v oracle-volume:/opt/oracle/oradata \
        my-custom-oracle-db:latest
docker: Error response from daemon: Conflict. The container name "/oracle-free" is already in use by container "c2e95a5dbbb4961521355745b67ab9f9eba6f4f83b8aeb69c380df290e025768". You have to remove (or rename) that container to be able to reuse that name.
See 'docker run --help'.
projectsuno@projects-MacBook-Pro docker % docker rm oracle-free
oracle-free
projectsuno@projects-MacBook-Pro docker % docker run -d --name=oracle-free \
        --network ${DOCKER_NETWORK} \
        -p 1521:1521 \
        -e ORACLE_PASSWORD=password \
        -v oracle-volume:/opt/oracle/oradata \
        my-custom-oracle-db:latest
7bdecf83386799525fb1991f146c9d0abcfe86946586e1fcb4459ade51c5f5d2
projectsuno@projects-MacBook-Pro docker % docker logs oracle-free
CONTAINER: starting up...
CONTAINER: first database startup, initializing...
CONTAINER: uncompressing database data files, please wait...


Break signaled
projectsuno@projects-MacBook-Pro docker % docker rm oracle-free
oracle-free
projectsuno@projects-MacBook-Pro docker %
projectsuno@projects-MacBook-Pro docker % docker volume rm oracle-volume
oracle-volume
projectsuno@projects-MacBook-Pro docker %
projectsuno@projects-MacBook-Pro docker %
projectsuno@projects-MacBook-Pro docker % docker run -d --name=oracle-free \
        --network ${DOCKER_NETWORK} \
        -p 1521:1521 \
        -e ORACLE_PASSWORD=password \
        -v oracle-volume:/opt/oracle/oradata \
        my-custom-oracle-db:latest
f572e95998f17937ae32914b08b2a76f4514593bc2587ab9c3307676ca188678
projectsuno@projects-MacBook-Pro docker %


https://stackoverflow.com/questions/65896681/exec-docker-credential-desktop-exe-executable-file-not-found-in-path


docker run -d --name=oracle-free \
--network ${DOCKER_NETWORK} \
-p 1521:1521 \
-v ORACLE_PASSWORD=password \
-v oracle-volume:/opt/oracle/oradata \
my-custom-oracle-db:latest
