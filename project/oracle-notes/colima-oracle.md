(base) avannala@Q2HWTCX6H4 Downloads % colima stop
INFO[0000] stopping colima
INFO[0000] stopping ...                                  context=docker
INFO[0017] stopping ...                                  context=vm
INFO[0025] done
(base) avannala@Q2HWTCX6H4 Downloads % colima start --arch x86_64 --memory 4 --network-address
INFO[0000] starting colima
INFO[0000] runtime: docker
Password:
INFO[0009] preparing network ...                         context=vm
INFO[0012] starting ...                                  context=vm
INFO[0083] provisioning ...                              context=docker
INFO[0091] starting ...                                  context=docker
INFO[0099] done
(base) avannala@Q2HWTCX6H4 Downloads % colima status
INFO[0002] colima is running using QEMU
INFO[0002] arch: x86_64
INFO[0002] runtime: docker
INFO[0002] mountType: sshfs
INFO[0002] address: 192.168.106.2
INFO[0002] socket: unix:///Users/avannala/.colima/default/docker.sock
(base) avannala@Q2HWTCX6H4 Downloads %






(base) avannala@Q2HWTCX6H4 Downloads % colima start --arch x86_64 --memory 4
WARN[0001] already running, ignoring
(base) avannala@Q2HWTCX6H4 Downloads % colima stop
INFO[0000] stopping colima
INFO[0000] stopping ...                                  context=docker
INFO[0004] stopping ...                                  context=vm
INFO[0007] done
(base) avannala@Q2HWTCX6H4 Downloads % colima start --arch x86_64 --memory 4

INFO[0001] starting colima
INFO[0001] runtime: docker
INFO[0002] starting ...                                  context=vm
INFO[0068] provisioning ...                              context=docker
INFO[0076] starting ...                                  context=docker
INFO[0083] done
(base) avannala@Q2HWTCX6H4 Downloads %
(base) avannala@Q2HWTCX6H4 Downloads % podman run -d --name=oracle-free -p 1521:1521 -e ORACLE_PASSWORD=password gvenzl/oracle-free
(base) avannala@Q2HWTCX6H4 Downloads %
(base) avannala@Q2HWTCX6H4 Downloads %
(base) avannala@Q2HWTCX6H4 Downloads % podman run -d --name=oracle-xe -p 1521:1521 -e ORACLE_PASSWORD=password -v oracle-volume:/opt/oracle/oradata gvenzl/oracle-xe

WARNING: image platform (linux/amd64) does not match the expected platform (linux/arm64)
b8c54f2047e89a3013e3973c32c005f20a95ac5bfb9abf5bcb1cb01b8070e8f3
(base) avannala@Q2HWTCX6H4 Downloads %
(base) avannala@Q2HWTCX6H4 Downloads %
(base) avannala@Q2HWTCX6H4 Downloads % docker run -d --name=oracle-xe -p 1521:1521 -e ORACLE_PASSWORD=password -v oracle-volume:/opt/oracle/oradata gvenzl/oracle-xe

Unable to find image 'gvenzl/oracle-xe:latest' locally
latest: Pulling from gvenzl/oracle-xe
db5c2b7644d0: Pull complete
f5cde12d8f01: Pull complete
871558e78a27: Pull complete
991bead44798: Pull complete
ba63154293b2: Pull complete
bb57cd9362b1: Pull complete
Digest: sha256:c2682a4216b0fe65537912c4a049c7e5c15a85bb7c94bb8137d5f2d2eef60603
Status: Downloaded newer image for gvenzl/oracle-xe:latest
1a8c9966fc7ec351cfc2afc98233293bef2376beab9240cc7b9250f5ac11c922
(base) avannala@Q2HWTCX6H4 Downloads % docker ps
CONTAINER ID   IMAGE              COMMAND                  CREATED              STATUS              PORTS                                         NAMES
1a8c9966fc7e   gvenzl/oracle-xe   "container-entrypoin…"   About a minute ago   Up About a minute   0.0.0.0:1521->1521/tcp, [::]:1521->1521/tcp   oracle-xe
(base) avannala@Q2HWTCX6H4 Downloads % docker stop oracle-xe
oracle-xe
(base) avannala@Q2HWTCX6H4 Downloads % docker rm oracle-xe
oracle-xe
(base) avannala@Q2HWTCX6H4 Downloads % docker run -d --name=oracle-free -p 1521:1521 -e ORACLE_PASSWORD=password -v oracle-volume:/opt/oracle/oradata gvenzl/oracle-xe

30110b4819b8219a03427ef11b5a81dc01bfe984af94511f63fccbe8590a5275
(base) avannala@Q2HWTCX6H4 Downloads % docker ps
CONTAINER ID   IMAGE              COMMAND                  CREATED         STATUS         PORTS                                         NAMES
30110b4819b8   gvenzl/oracle-xe   "container-entrypoin…"   5 seconds ago   Up 2 seconds   0.0.0.0:1521->1521/tcp, [::]:1521->1521/tcp   oracle-free
(base) avannala@Q2HWTCX6H4 Downloads %
(base) avannala@Q2HWTCX6H4 Downloads %
(base) avannala@Q2HWTCX6H4 Downloads %