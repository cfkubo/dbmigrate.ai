multipass transfer -r spf-converter docker-build:spf-converter

multipass transfer docker-build:spf-converter/spf-converter.tar.gz .

######

(base) avannala@Q2HWTCX6H4 workspace % multipass transfer -r spf-converter docker-build:spf-converter
(base) avannala@Q2HWTCX6H4 workspace % multipass shell docker-build
Welcome to Ubuntu 24.04.3 LTS (GNU/Linux 6.8.0-71-generic aarch64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Wed Sep 24 20:31:26 MDT 2025

  System load:             0.01
  Usage of /:              24.5% of 18.33GB
  Memory usage:            20%
  Swap usage:              0%
  Processes:               106
  Users logged in:         0
  IPv4 address for enp0s1: 192.168.106.8
  IPv6 address for enp0s1: fdf1:d7c:9e11:3f34:5054:ff:fee6:6747


Expanded Security Maintenance for Applications is not enabled.

52 updates can be applied immediately.
38 of these updates are standard security updates.
To see these additional updates run: apt list --upgradable

1 additional security update can be applied with ESM Apps.
Learn more about enabling ESM Apps service at https://ubuntu.com/esm


Last login: Wed Sep 24 20:31:27 2025 from 192.168.106.1
ubuntu@docker-build:~$ cd spf-converter/
ubuntu@docker-build:~/spf-converter$ cd docker/
ubuntu@docker-build:~/spf-converter/docker$ ll
total 32
drwxr-xr-x  2 ubuntu ubuntu 4096 Sep 24 20:31 ./
drwxr-xr-x 13 ubuntu ubuntu 4096 Sep 24 20:31 ../
-rw-r--r--  1 ubuntu ubuntu  785 Sep 24 20:31 Dockerfile
-rw-r--r--  1 ubuntu ubuntu  822 Sep 24 20:31 Dockerfile_arul
-rw-r--r--  1 ubuntu ubuntu 1005 Sep 24 20:31 Dockerfile_new
-rw-r--r--  1 ubuntu ubuntu 1622 Sep 24 20:31 docker-compose.yml
-rw-r--r--  1 ubuntu ubuntu 1300 Sep 24 20:31 docker-container.md
-rw-r--r--  1 ubuntu ubuntu   89 Sep 24 20:31 docker.md
ubuntu@docker-build:~/spf-converter/docker$ sudo docker build -f Dockerfile  -t spf-converter:latest .
DEPRECATED: The legacy builder is deprecated and will be removed in a future release.
            Install the buildx component to build images with BuildKit:
            https://docs.docker.com/go/buildx/

Sending build context to Docker daemon  11.26kB
Step 1/11 : FROM --platform=arm64 python:3.12-slim
 ---> 12201b64d1f1
Step 2/11 : ENV PYTHONDONTWRITEBYTECODE=1
 ---> Using cache
 ---> 7d3306c5a83d
Step 3/11 : ENV PYTHONUNBUFFERED=1
 ---> Using cache
 ---> 3c1cd2e85a50
Step 4/11 : WORKDIR /app
 ---> Using cache
 ---> e4e0ad5dc0f7
Step 5/11 : RUN apt-get update && apt-get install -y --no-install-recommends     build-essential     gcc     libpq-dev     ca-certificates     && rm -rf /var/lib/apt/lists/*
 ---> Using cache
 ---> bcc2ea5b5762
Step 6/11 : COPY ../requirements.txt  requirements.txt
COPY failed: forbidden path outside the build context: ../requirements.txt ()
ubuntu@docker-build:~/spf-converter/docker$
ubuntu@docker-build:~/spf-converter/docker$
ubuntu@docker-build:~/spf-converter/docker$
ubuntu@docker-build:~/spf-converter/docker$ pwd
/home/ubuntu/spf-converter/docker
ubuntu@docker-build:~/spf-converter/docker$ ls ../re
reprocess_dlq.py  requirements.txt
ubuntu@docker-build:~/spf-converter/docker$ ls ../re
reprocess_dlq.py  requirements.txt
ubuntu@docker-build:~/spf-converter/docker$ ls ../requirements.txt
../requirements.txt
ubuntu@docker-build:~/spf-converter/docker$ cd ..
ubuntu@docker-build:~/spf-converter$
ubuntu@docker-build:~/spf-converter$ sudo docker build -f Dockerfile  -t spf-converter:latest .
DEPRECATED: The legacy builder is deprecated and will be removed in a future release.
            Install the buildx component to build images with BuildKit:
            https://docs.docker.com/go/buildx/

Sending build context to Docker daemon  462.8MB
Step 1/11 : FROM python:3.11-slim
3.11-slim: Pulling from library/python
b2feff975e6d: Already exists
440ff9e33d74: Pull complete
0dc0d0d23e1f: Pull complete
e9246f522e03: Pull complete
Digest: sha256:a0939570b38cddeb861b8e75d20b1c8218b21562b18f301171904b544e8cf228
Status: Downloaded newer image for python:3.11-slim
 ---> 43c52b5ca8dc
Step 2/11 : ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1
 ---> Running in f4660ee3e503
 ---> Removed intermediate container f4660ee3e503
 ---> 03c2a42bad8b
Step 3/11 : WORKDIR /app
 ---> Running in 957bf8e86411
 ---> Removed intermediate container 957bf8e86411
 ---> a5ace308c9e6
Step 4/11 : RUN apt-get update && apt-get install -y --no-install-recommends     build-essential     gcc     libpq-dev     ca-certificates     && rm -rf /var/lib/apt/lists/*
 ---> Running in 5179429fae40
Hit:1 http://deb.debian.org/debian trixie InRelease
Get:2 http://deb.debian.org/debian trixie-updates InRelease [47.3 kB]
Get:3 http://deb.debian.org/debian-security trixie-security InRelease [43.4 kB]
Get:4 http://deb.debian.org/debian trixie/main arm64 Packages [9605 kB]
Get:5 http://deb.debian.org/debian trixie-updates/main arm64 Packages [5404 B]
Get:6 http://deb.debian.org/debian-security trixie-security/main arm64 Packages [46.4 kB]
Fetched 9747 kB in 1s (6560 kB/s)
Reading package lists...
Reading package lists...
Building dependency tree...
Reading state information...
ca-certificates is already the newest version (20250419).
The following additional packages will be installed:
  binutils binutils-aarch64-linux-gnu binutils-common bzip2 cpp cpp-14
  cpp-14-aarch64-linux-gnu cpp-aarch64-linux-gnu dpkg-dev g++ g++-14
  g++-14-aarch64-linux-gnu g++-aarch64-linux-gnu gcc-14
  gcc-14-aarch64-linux-gnu gcc-aarch64-linux-gnu libasan8 libatomic1
  libbinutils libc-dev-bin libc6-dev libcc1-0 libcom-err2 libcrypt-dev
  libctf-nobfd0 libctf0 libdpkg-perl libgcc-14-dev libgdbm-compat4t64 libgomp1
  libgprofng0 libgssapi-krb5-2 libhwasan0 libisl23 libitm1 libjansson4
  libk5crypto3 libkeyutils1 libkrb5-3 libkrb5support0 libldap2 liblsan0
  libmpc3 libmpfr6 libperl5.40 libpq5 libsasl2-2 libsasl2-modules-db
  libsframe1 libssl-dev libstdc++-14-dev libtsan2 libubsan1 linux-libc-dev
  make patch perl perl-modules-5.40 rpcsvc-proto xz-utils
Suggested packages:
  binutils-doc gprofng-gui binutils-gold bzip2-doc cpp-doc gcc-14-locales
  cpp-14-doc debian-keyring debian-tag2upload-keyring gcc-14-doc gcc-multilib
  manpages-dev autoconf automake libtool flex bison gdb gcc-doc
  gdb-aarch64-linux-gnu libc-devtools glibc-doc sq | sqop | rsop | gosop
  | pgpainless-cli | gpg-sq | gnupg sensible-utils git bzr krb5-doc krb5-user
  postgresql-doc-17 libssl-doc libstdc++-14-doc make-doc ed diffutils-doc
  perl-doc libterm-readline-gnu-perl | libterm-readline-perl-perl
  libtap-harness-archive-perl
Recommended packages:
  fakeroot sq | sqop | rsop | gosop | pgpainless-cli | gpg-sq | gnupg
  libalgorithm-merge-perl manpages manpages-dev libfile-fcntllock-perl
  liblocale-gettext-perl krb5-locales libldap-common libsasl2-modules
The following NEW packages will be installed:
  binutils binutils-aarch64-linux-gnu binutils-common build-essential bzip2
  cpp cpp-14 cpp-14-aarch64-linux-gnu cpp-aarch64-linux-gnu dpkg-dev g++
  g++-14 g++-14-aarch64-linux-gnu g++-aarch64-linux-gnu gcc gcc-14
  gcc-14-aarch64-linux-gnu gcc-aarch64-linux-gnu libasan8 libatomic1
  libbinutils libc-dev-bin libc6-dev libcc1-0 libcom-err2 libcrypt-dev
  libctf-nobfd0 libctf0 libdpkg-perl libgcc-14-dev libgdbm-compat4t64 libgomp1
  libgprofng0 libgssapi-krb5-2 libhwasan0 libisl23 libitm1 libjansson4
  libk5crypto3 libkeyutils1 libkrb5-3 libkrb5support0 libldap2 liblsan0
  libmpc3 libmpfr6 libperl5.40 libpq-dev libpq5 libsasl2-2 libsasl2-modules-db
  libsframe1 libssl-dev libstdc++-14-dev libtsan2 libubsan1 linux-libc-dev
  make patch perl perl-modules-5.40 rpcsvc-proto xz-utils
0 upgraded, 63 newly installed, 0 to remove and 2 not upgraded.
Need to get 77.4 MB of archives.
After this operation, 344 MB of additional disk space will be used.
Get:1 http://deb.debian.org/debian trixie/main arm64 bzip2 arm64 1.0.8-6 [39.5 kB]
Get:2 http://deb.debian.org/debian trixie/main arm64 perl-modules-5.40 all 5.40.1-6 [3019 kB]
Get:3 http://deb.debian.org/debian trixie/main arm64 libgdbm-compat4t64 arm64 1.24-2 [50.3 kB]
Get:4 http://deb.debian.org/debian trixie/main arm64 libperl5.40 arm64 5.40.1-6 [4142 kB]
Get:5 http://deb.debian.org/debian trixie/main arm64 perl arm64 5.40.1-6 [267 kB]
Get:6 http://deb.debian.org/debian trixie/main arm64 xz-utils arm64 5.8.1-1 [657 kB]
Get:7 http://deb.debian.org/debian trixie/main arm64 libsframe1 arm64 2.44-3 [77.8 kB]
Get:8 http://deb.debian.org/debian trixie/main arm64 binutils-common arm64 2.44-3 [2509 kB]
Get:9 http://deb.debian.org/debian trixie/main arm64 libbinutils arm64 2.44-3 [660 kB]
Get:10 http://deb.debian.org/debian trixie/main arm64 libgprofng0 arm64 2.44-3 [668 kB]
Get:11 http://deb.debian.org/debian trixie/main arm64 libctf-nobfd0 arm64 2.44-3 [152 kB]
Get:12 http://deb.debian.org/debian trixie/main arm64 libctf0 arm64 2.44-3 [84.2 kB]
Get:13 http://deb.debian.org/debian trixie/main arm64 libjansson4 arm64 2.14-2+b3 [39.2 kB]
Get:14 http://deb.debian.org/debian trixie/main arm64 binutils-aarch64-linux-gnu arm64 2.44-3 [820 kB]
Get:15 http://deb.debian.org/debian trixie/main arm64 binutils arm64 2.44-3 [262 kB]
Get:16 http://deb.debian.org/debian trixie/main arm64 libc-dev-bin arm64 2.41-12 [57.4 kB]
Get:17 http://deb.debian.org/debian-security trixie-security/main arm64 linux-libc-dev all 6.12.48-1 [2671 kB]
Get:18 http://deb.debian.org/debian trixie/main arm64 libcrypt-dev arm64 1:4.4.38-1 [123 kB]
Get:19 http://deb.debian.org/debian trixie/main arm64 rpcsvc-proto arm64 1.4.3-1+b1 [60.5 kB]
Get:20 http://deb.debian.org/debian trixie/main arm64 libc6-dev arm64 2.41-12 [1621 kB]
Get:21 http://deb.debian.org/debian trixie/main arm64 libisl23 arm64 0.27-1 [601 kB]
Get:22 http://deb.debian.org/debian trixie/main arm64 libmpfr6 arm64 4.2.2-1 [685 kB]
Get:23 http://deb.debian.org/debian trixie/main arm64 libmpc3 arm64 1.3.1-1+b3 [50.5 kB]
Get:24 http://deb.debian.org/debian trixie/main arm64 cpp-14-aarch64-linux-gnu arm64 14.2.0-19 [9169 kB]
Get:25 http://deb.debian.org/debian trixie/main arm64 cpp-14 arm64 14.2.0-19 [1276 B]
Get:26 http://deb.debian.org/debian trixie/main arm64 cpp-aarch64-linux-gnu arm64 4:14.2.0-1 [4832 B]
Get:27 http://deb.debian.org/debian trixie/main arm64 cpp arm64 4:14.2.0-1 [1568 B]
Get:28 http://deb.debian.org/debian trixie/main arm64 libcc1-0 arm64 14.2.0-19 [42.2 kB]
Get:29 http://deb.debian.org/debian trixie/main arm64 libgomp1 arm64 14.2.0-19 [124 kB]
Get:30 http://deb.debian.org/debian trixie/main arm64 libitm1 arm64 14.2.0-19 [24.2 kB]
Get:31 http://deb.debian.org/debian trixie/main arm64 libatomic1 arm64 14.2.0-19 [10.1 kB]
Get:32 http://deb.debian.org/debian trixie/main arm64 libasan8 arm64 14.2.0-19 [2578 kB]
Get:33 http://deb.debian.org/debian trixie/main arm64 liblsan0 arm64 14.2.0-19 [1161 kB]
Get:34 http://deb.debian.org/debian trixie/main arm64 libtsan2 arm64 14.2.0-19 [2383 kB]
Get:35 http://deb.debian.org/debian trixie/main arm64 libubsan1 arm64 14.2.0-19 [1039 kB]
Get:36 http://deb.debian.org/debian trixie/main arm64 libhwasan0 arm64 14.2.0-19 [1442 kB]
Get:37 http://deb.debian.org/debian trixie/main arm64 libgcc-14-dev arm64 14.2.0-19 [2359 kB]
Get:38 http://deb.debian.org/debian trixie/main arm64 gcc-14-aarch64-linux-gnu arm64 14.2.0-19 [17.7 MB]
Get:39 http://deb.debian.org/debian trixie/main arm64 gcc-14 arm64 14.2.0-19 [529 kB]
Get:40 http://deb.debian.org/debian trixie/main arm64 gcc-aarch64-linux-gnu arm64 4:14.2.0-1 [1440 B]
Get:41 http://deb.debian.org/debian trixie/main arm64 gcc arm64 4:14.2.0-1 [5136 B]
Get:42 http://deb.debian.org/debian trixie/main arm64 libstdc++-14-dev arm64 14.2.0-19 [2295 kB]
Get:43 http://deb.debian.org/debian trixie/main arm64 g++-14-aarch64-linux-gnu arm64 14.2.0-19 [10.1 MB]
Get:44 http://deb.debian.org/debian trixie/main arm64 g++-14 arm64 14.2.0-19 [22.5 kB]
Get:45 http://deb.debian.org/debian trixie/main arm64 g++-aarch64-linux-gnu arm64 4:14.2.0-1 [1200 B]
Get:46 http://deb.debian.org/debian trixie/main arm64 g++ arm64 4:14.2.0-1 [1332 B]
Get:47 http://deb.debian.org/debian trixie/main arm64 make arm64 4.4.1-2 [452 kB]
Get:48 http://deb.debian.org/debian trixie/main arm64 libdpkg-perl all 1.22.21 [650 kB]
Get:49 http://deb.debian.org/debian trixie/main arm64 patch arm64 2.8-2 [128 kB]
Get:50 http://deb.debian.org/debian trixie/main arm64 dpkg-dev all 1.22.21 [1338 kB]
Get:51 http://deb.debian.org/debian trixie/main arm64 build-essential arm64 12.12 [4624 B]
Get:52 http://deb.debian.org/debian trixie/main arm64 libcom-err2 arm64 1.47.2-3+b3 [24.9 kB]
Get:53 http://deb.debian.org/debian trixie/main arm64 libkrb5support0 arm64 1.21.3-5 [32.4 kB]
Get:54 http://deb.debian.org/debian trixie/main arm64 libk5crypto3 arm64 1.21.3-5 [81.2 kB]
Get:55 http://deb.debian.org/debian trixie/main arm64 libkeyutils1 arm64 1.6.3-6 [9716 B]
Get:56 http://deb.debian.org/debian trixie/main arm64 libkrb5-3 arm64 1.21.3-5 [308 kB]
Get:57 http://deb.debian.org/debian trixie/main arm64 libgssapi-krb5-2 arm64 1.21.3-5 [127 kB]
Get:58 http://deb.debian.org/debian trixie/main arm64 libsasl2-modules-db arm64 2.1.28+dfsg1-9 [20.1 kB]
Get:59 http://deb.debian.org/debian trixie/main arm64 libsasl2-2 arm64 2.1.28+dfsg1-9 [55.6 kB]
Get:60 http://deb.debian.org/debian trixie/main arm64 libldap2 arm64 2.6.10+dfsg-1 [179 kB]
Get:61 http://deb.debian.org/debian trixie/main arm64 libpq5 arm64 17.6-0+deb13u1 [220 kB]
Get:62 http://deb.debian.org/debian trixie/main arm64 libssl-dev arm64 3.5.1-1 [3385 kB]
Get:63 http://deb.debian.org/debian trixie/main arm64 libpq-dev arm64 17.6-0+deb13u1 [147 kB]
debconf: unable to initialize frontend: Dialog
debconf: (TERM is not set, so the dialog frontend is not usable.)
debconf: falling back to frontend: Readline
debconf: unable to initialize frontend: Readline
debconf: (Can't locate Term/ReadLine.pm in @INC (you may need to install the Term::ReadLine module) (@INC entries checked: /etc/perl /usr/local/lib/aarch64-linux-gnu/perl/5.40.1 /usr/local/share/perl/5.40.1 /usr/lib/aarch64-linux-gnu/perl5/5.40 /usr/share/perl5 /usr/lib/aarch64-linux-gnu/perl-base /usr/lib/aarch64-linux-gnu/perl/5.40 /usr/share/perl/5.40 /usr/local/lib/site_perl) at /usr/share/perl5/Debconf/FrontEnd/Readline.pm line 8, <STDIN> line 63.)
debconf: falling back to frontend: Teletype
debconf: unable to initialize frontend: Teletype
debconf: (This frontend requires a controlling tty.)
debconf: falling back to frontend: Noninteractive
Fetched 77.4 MB in 1s (60.4 MB/s)
Selecting previously unselected package bzip2.
(Reading database ... 5642 files and directories currently installed.)
Preparing to unpack .../00-bzip2_1.0.8-6_arm64.deb ...
Unpacking bzip2 (1.0.8-6) ...
Selecting previously unselected package perl-modules-5.40.
Preparing to unpack .../01-perl-modules-5.40_5.40.1-6_all.deb ...
Unpacking perl-modules-5.40 (5.40.1-6) ...
Selecting previously unselected package libgdbm-compat4t64:arm64.
Preparing to unpack .../02-libgdbm-compat4t64_1.24-2_arm64.deb ...
Unpacking libgdbm-compat4t64:arm64 (1.24-2) ...
Selecting previously unselected package libperl5.40:arm64.
Preparing to unpack .../03-libperl5.40_5.40.1-6_arm64.deb ...
Unpacking libperl5.40:arm64 (5.40.1-6) ...
Selecting previously unselected package perl.
Preparing to unpack .../04-perl_5.40.1-6_arm64.deb ...
Unpacking perl (5.40.1-6) ...
Selecting previously unselected package xz-utils.
Preparing to unpack .../05-xz-utils_5.8.1-1_arm64.deb ...
Unpacking xz-utils (5.8.1-1) ...
Selecting previously unselected package libsframe1:arm64.
Preparing to unpack .../06-libsframe1_2.44-3_arm64.deb ...
Unpacking libsframe1:arm64 (2.44-3) ...
Selecting previously unselected package binutils-common:arm64.
Preparing to unpack .../07-binutils-common_2.44-3_arm64.deb ...
Unpacking binutils-common:arm64 (2.44-3) ...
Selecting previously unselected package libbinutils:arm64.
Preparing to unpack .../08-libbinutils_2.44-3_arm64.deb ...
Unpacking libbinutils:arm64 (2.44-3) ...
Selecting previously unselected package libgprofng0:arm64.
Preparing to unpack .../09-libgprofng0_2.44-3_arm64.deb ...
Unpacking libgprofng0:arm64 (2.44-3) ...
Selecting previously unselected package libctf-nobfd0:arm64.
Preparing to unpack .../10-libctf-nobfd0_2.44-3_arm64.deb ...
Unpacking libctf-nobfd0:arm64 (2.44-3) ...
Selecting previously unselected package libctf0:arm64.
Preparing to unpack .../11-libctf0_2.44-3_arm64.deb ...
Unpacking libctf0:arm64 (2.44-3) ...
Selecting previously unselected package libjansson4:arm64.
Preparing to unpack .../12-libjansson4_2.14-2+b3_arm64.deb ...
Unpacking libjansson4:arm64 (2.14-2+b3) ...
Selecting previously unselected package binutils-aarch64-linux-gnu.
Preparing to unpack .../13-binutils-aarch64-linux-gnu_2.44-3_arm64.deb ...
Unpacking binutils-aarch64-linux-gnu (2.44-3) ...
Selecting previously unselected package binutils.
Preparing to unpack .../14-binutils_2.44-3_arm64.deb ...
Unpacking binutils (2.44-3) ...
Selecting previously unselected package libc-dev-bin.
Preparing to unpack .../15-libc-dev-bin_2.41-12_arm64.deb ...
Unpacking libc-dev-bin (2.41-12) ...
Selecting previously unselected package linux-libc-dev.
Preparing to unpack .../16-linux-libc-dev_6.12.48-1_all.deb ...
Unpacking linux-libc-dev (6.12.48-1) ...
Selecting previously unselected package libcrypt-dev:arm64.
Preparing to unpack .../17-libcrypt-dev_1%3a4.4.38-1_arm64.deb ...
Unpacking libcrypt-dev:arm64 (1:4.4.38-1) ...
Selecting previously unselected package rpcsvc-proto.
Preparing to unpack .../18-rpcsvc-proto_1.4.3-1+b1_arm64.deb ...
Unpacking rpcsvc-proto (1.4.3-1+b1) ...
Selecting previously unselected package libc6-dev:arm64.
Preparing to unpack .../19-libc6-dev_2.41-12_arm64.deb ...
Unpacking libc6-dev:arm64 (2.41-12) ...
Selecting previously unselected package libisl23:arm64.
Preparing to unpack .../20-libisl23_0.27-1_arm64.deb ...
Unpacking libisl23:arm64 (0.27-1) ...
Selecting previously unselected package libmpfr6:arm64.
Preparing to unpack .../21-libmpfr6_4.2.2-1_arm64.deb ...
Unpacking libmpfr6:arm64 (4.2.2-1) ...
Selecting previously unselected package libmpc3:arm64.
Preparing to unpack .../22-libmpc3_1.3.1-1+b3_arm64.deb ...
Unpacking libmpc3:arm64 (1.3.1-1+b3) ...
Selecting previously unselected package cpp-14-aarch64-linux-gnu.
Preparing to unpack .../23-cpp-14-aarch64-linux-gnu_14.2.0-19_arm64.deb ...
Unpacking cpp-14-aarch64-linux-gnu (14.2.0-19) ...
Selecting previously unselected package cpp-14.
Preparing to unpack .../24-cpp-14_14.2.0-19_arm64.deb ...
Unpacking cpp-14 (14.2.0-19) ...
Selecting previously unselected package cpp-aarch64-linux-gnu.
Preparing to unpack .../25-cpp-aarch64-linux-gnu_4%3a14.2.0-1_arm64.deb ...
Unpacking cpp-aarch64-linux-gnu (4:14.2.0-1) ...
Selecting previously unselected package cpp.
Preparing to unpack .../26-cpp_4%3a14.2.0-1_arm64.deb ...
Unpacking cpp (4:14.2.0-1) ...
Selecting previously unselected package libcc1-0:arm64.
Preparing to unpack .../27-libcc1-0_14.2.0-19_arm64.deb ...
Unpacking libcc1-0:arm64 (14.2.0-19) ...
Selecting previously unselected package libgomp1:arm64.
Preparing to unpack .../28-libgomp1_14.2.0-19_arm64.deb ...
Unpacking libgomp1:arm64 (14.2.0-19) ...
Selecting previously unselected package libitm1:arm64.
Preparing to unpack .../29-libitm1_14.2.0-19_arm64.deb ...
Unpacking libitm1:arm64 (14.2.0-19) ...
Selecting previously unselected package libatomic1:arm64.
Preparing to unpack .../30-libatomic1_14.2.0-19_arm64.deb ...
Unpacking libatomic1:arm64 (14.2.0-19) ...
Selecting previously unselected package libasan8:arm64.
Preparing to unpack .../31-libasan8_14.2.0-19_arm64.deb ...
Unpacking libasan8:arm64 (14.2.0-19) ...
Selecting previously unselected package liblsan0:arm64.
Preparing to unpack .../32-liblsan0_14.2.0-19_arm64.deb ...
Unpacking liblsan0:arm64 (14.2.0-19) ...
Selecting previously unselected package libtsan2:arm64.
Preparing to unpack .../33-libtsan2_14.2.0-19_arm64.deb ...
Unpacking libtsan2:arm64 (14.2.0-19) ...
Selecting previously unselected package libubsan1:arm64.
Preparing to unpack .../34-libubsan1_14.2.0-19_arm64.deb ...
Unpacking libubsan1:arm64 (14.2.0-19) ...
Selecting previously unselected package libhwasan0:arm64.
Preparing to unpack .../35-libhwasan0_14.2.0-19_arm64.deb ...
Unpacking libhwasan0:arm64 (14.2.0-19) ...
Selecting previously unselected package libgcc-14-dev:arm64.
Preparing to unpack .../36-libgcc-14-dev_14.2.0-19_arm64.deb ...
Unpacking libgcc-14-dev:arm64 (14.2.0-19) ...
Selecting previously unselected package gcc-14-aarch64-linux-gnu.
Preparing to unpack .../37-gcc-14-aarch64-linux-gnu_14.2.0-19_arm64.deb ...
Unpacking gcc-14-aarch64-linux-gnu (14.2.0-19) ...
Selecting previously unselected package gcc-14.
Preparing to unpack .../38-gcc-14_14.2.0-19_arm64.deb ...
Unpacking gcc-14 (14.2.0-19) ...
Selecting previously unselected package gcc-aarch64-linux-gnu.
Preparing to unpack .../39-gcc-aarch64-linux-gnu_4%3a14.2.0-1_arm64.deb ...
Unpacking gcc-aarch64-linux-gnu (4:14.2.0-1) ...
Selecting previously unselected package gcc.
Preparing to unpack .../40-gcc_4%3a14.2.0-1_arm64.deb ...
Unpacking gcc (4:14.2.0-1) ...
Selecting previously unselected package libstdc++-14-dev:arm64.
Preparing to unpack .../41-libstdc++-14-dev_14.2.0-19_arm64.deb ...
Unpacking libstdc++-14-dev:arm64 (14.2.0-19) ...
Selecting previously unselected package g++-14-aarch64-linux-gnu.
Preparing to unpack .../42-g++-14-aarch64-linux-gnu_14.2.0-19_arm64.deb ...
Unpacking g++-14-aarch64-linux-gnu (14.2.0-19) ...
Selecting previously unselected package g++-14.
Preparing to unpack .../43-g++-14_14.2.0-19_arm64.deb ...
Unpacking g++-14 (14.2.0-19) ...
Selecting previously unselected package g++-aarch64-linux-gnu.
Preparing to unpack .../44-g++-aarch64-linux-gnu_4%3a14.2.0-1_arm64.deb ...
Unpacking g++-aarch64-linux-gnu (4:14.2.0-1) ...
Selecting previously unselected package g++.
Preparing to unpack .../45-g++_4%3a14.2.0-1_arm64.deb ...
Unpacking g++ (4:14.2.0-1) ...
Selecting previously unselected package make.
Preparing to unpack .../46-make_4.4.1-2_arm64.deb ...
Unpacking make (4.4.1-2) ...
Selecting previously unselected package libdpkg-perl.
Preparing to unpack .../47-libdpkg-perl_1.22.21_all.deb ...
Unpacking libdpkg-perl (1.22.21) ...
Selecting previously unselected package patch.
Preparing to unpack .../48-patch_2.8-2_arm64.deb ...
Unpacking patch (2.8-2) ...
Selecting previously unselected package dpkg-dev.
Preparing to unpack .../49-dpkg-dev_1.22.21_all.deb ...
Unpacking dpkg-dev (1.22.21) ...
Selecting previously unselected package build-essential.
Preparing to unpack .../50-build-essential_12.12_arm64.deb ...
Unpacking build-essential (12.12) ...
Selecting previously unselected package libcom-err2:arm64.
Preparing to unpack .../51-libcom-err2_1.47.2-3+b3_arm64.deb ...
Unpacking libcom-err2:arm64 (1.47.2-3+b3) ...
Selecting previously unselected package libkrb5support0:arm64.
Preparing to unpack .../52-libkrb5support0_1.21.3-5_arm64.deb ...
Unpacking libkrb5support0:arm64 (1.21.3-5) ...
Selecting previously unselected package libk5crypto3:arm64.
Preparing to unpack .../53-libk5crypto3_1.21.3-5_arm64.deb ...
Unpacking libk5crypto3:arm64 (1.21.3-5) ...
Selecting previously unselected package libkeyutils1:arm64.
Preparing to unpack .../54-libkeyutils1_1.6.3-6_arm64.deb ...
Unpacking libkeyutils1:arm64 (1.6.3-6) ...
Selecting previously unselected package libkrb5-3:arm64.
Preparing to unpack .../55-libkrb5-3_1.21.3-5_arm64.deb ...
Unpacking libkrb5-3:arm64 (1.21.3-5) ...
Selecting previously unselected package libgssapi-krb5-2:arm64.
Preparing to unpack .../56-libgssapi-krb5-2_1.21.3-5_arm64.deb ...
Unpacking libgssapi-krb5-2:arm64 (1.21.3-5) ...
Selecting previously unselected package libsasl2-modules-db:arm64.
Preparing to unpack .../57-libsasl2-modules-db_2.1.28+dfsg1-9_arm64.deb ...
Unpacking libsasl2-modules-db:arm64 (2.1.28+dfsg1-9) ...
Selecting previously unselected package libsasl2-2:arm64.
Preparing to unpack .../58-libsasl2-2_2.1.28+dfsg1-9_arm64.deb ...
Unpacking libsasl2-2:arm64 (2.1.28+dfsg1-9) ...
Selecting previously unselected package libldap2:arm64.
Preparing to unpack .../59-libldap2_2.6.10+dfsg-1_arm64.deb ...
Unpacking libldap2:arm64 (2.6.10+dfsg-1) ...
Selecting previously unselected package libpq5:arm64.
Preparing to unpack .../60-libpq5_17.6-0+deb13u1_arm64.deb ...
Unpacking libpq5:arm64 (17.6-0+deb13u1) ...
Selecting previously unselected package libssl-dev:arm64.
Preparing to unpack .../61-libssl-dev_3.5.1-1_arm64.deb ...
Unpacking libssl-dev:arm64 (3.5.1-1) ...
Selecting previously unselected package libpq-dev.
Preparing to unpack .../62-libpq-dev_17.6-0+deb13u1_arm64.deb ...
Unpacking libpq-dev (17.6-0+deb13u1) ...
Setting up libkeyutils1:arm64 (1.6.3-6) ...
Setting up libgdbm-compat4t64:arm64 (1.24-2) ...
Setting up binutils-common:arm64 (2.44-3) ...
Setting up linux-libc-dev (6.12.48-1) ...
Setting up libctf-nobfd0:arm64 (2.44-3) ...
Setting up libcom-err2:arm64 (1.47.2-3+b3) ...
Setting up libgomp1:arm64 (14.2.0-19) ...
Setting up bzip2 (1.0.8-6) ...
Setting up libsframe1:arm64 (2.44-3) ...
Setting up libjansson4:arm64 (2.14-2+b3) ...
Setting up libkrb5support0:arm64 (1.21.3-5) ...
Setting up libsasl2-modules-db:arm64 (2.1.28+dfsg1-9) ...
Setting up rpcsvc-proto (1.4.3-1+b1) ...
Setting up make (4.4.1-2) ...
Setting up libmpfr6:arm64 (4.2.2-1) ...
Setting up xz-utils (5.8.1-1) ...
update-alternatives: using /usr/bin/xz to provide /usr/bin/lzma (lzma) in auto mode
update-alternatives: warning: skip creation of /usr/share/man/man1/lzma.1.gz because associated file /usr/share/man/man1/xz.1.gz (of link group lzma) doesn't exist
update-alternatives: warning: skip creation of /usr/share/man/man1/unlzma.1.gz because associated file /usr/share/man/man1/unxz.1.gz (of link group lzma) doesn't exist
update-alternatives: warning: skip creation of /usr/share/man/man1/lzcat.1.gz because associated file /usr/share/man/man1/xzcat.1.gz (of link group lzma) doesn't exist
update-alternatives: warning: skip creation of /usr/share/man/man1/lzmore.1.gz because associated file /usr/share/man/man1/xzmore.1.gz (of link group lzma) doesn't exist
update-alternatives: warning: skip creation of /usr/share/man/man1/lzless.1.gz because associated file /usr/share/man/man1/xzless.1.gz (of link group lzma) doesn't exist
update-alternatives: warning: skip creation of /usr/share/man/man1/lzdiff.1.gz because associated file /usr/share/man/man1/xzdiff.1.gz (of link group lzma) doesn't exist
update-alternatives: warning: skip creation of /usr/share/man/man1/lzcmp.1.gz because associated file /usr/share/man/man1/xzcmp.1.gz (of link group lzma) doesn't exist
update-alternatives: warning: skip creation of /usr/share/man/man1/lzgrep.1.gz because associated file /usr/share/man/man1/xzgrep.1.gz (of link group lzma) doesn't exist
update-alternatives: warning: skip creation of /usr/share/man/man1/lzegrep.1.gz because associated file /usr/share/man/man1/xzegrep.1.gz (of link group lzma) doesn't exist
update-alternatives: warning: skip creation of /usr/share/man/man1/lzfgrep.1.gz because associated file /usr/share/man/man1/xzfgrep.1.gz (of link group lzma) doesn't exist
Setting up libssl-dev:arm64 (3.5.1-1) ...
Setting up libmpc3:arm64 (1.3.1-1+b3) ...
Setting up libatomic1:arm64 (14.2.0-19) ...
Setting up patch (2.8-2) ...
Setting up libk5crypto3:arm64 (1.21.3-5) ...
Setting up libsasl2-2:arm64 (2.1.28+dfsg1-9) ...
Setting up libubsan1:arm64 (14.2.0-19) ...
Setting up perl-modules-5.40 (5.40.1-6) ...
Setting up libhwasan0:arm64 (14.2.0-19) ...
Setting up libcrypt-dev:arm64 (1:4.4.38-1) ...
Setting up libasan8:arm64 (14.2.0-19) ...
Setting up libkrb5-3:arm64 (1.21.3-5) ...
Setting up libtsan2:arm64 (14.2.0-19) ...
Setting up libbinutils:arm64 (2.44-3) ...
Setting up libisl23:arm64 (0.27-1) ...
Setting up libc-dev-bin (2.41-12) ...
Setting up libcc1-0:arm64 (14.2.0-19) ...
Setting up libldap2:arm64 (2.6.10+dfsg-1) ...
Setting up liblsan0:arm64 (14.2.0-19) ...
Setting up libitm1:arm64 (14.2.0-19) ...
Setting up libctf0:arm64 (2.44-3) ...
Setting up binutils-aarch64-linux-gnu (2.44-3) ...
Setting up libperl5.40:arm64 (5.40.1-6) ...
Setting up perl (5.40.1-6) ...
Setting up libgprofng0:arm64 (2.44-3) ...
Setting up libgssapi-krb5-2:arm64 (1.21.3-5) ...
Setting up libdpkg-perl (1.22.21) ...
Setting up cpp-14-aarch64-linux-gnu (14.2.0-19) ...
Setting up libc6-dev:arm64 (2.41-12) ...
Setting up libgcc-14-dev:arm64 (14.2.0-19) ...
Setting up libstdc++-14-dev:arm64 (14.2.0-19) ...
Setting up libpq5:arm64 (17.6-0+deb13u1) ...
Setting up libpq-dev (17.6-0+deb13u1) ...
Setting up binutils (2.44-3) ...
Setting up dpkg-dev (1.22.21) ...
Setting up cpp-aarch64-linux-gnu (4:14.2.0-1) ...
Setting up cpp-14 (14.2.0-19) ...
Setting up cpp (4:14.2.0-1) ...
Setting up gcc-14-aarch64-linux-gnu (14.2.0-19) ...
Setting up gcc-aarch64-linux-gnu (4:14.2.0-1) ...
Setting up g++-14-aarch64-linux-gnu (14.2.0-19) ...
Setting up gcc-14 (14.2.0-19) ...
Setting up g++-aarch64-linux-gnu (4:14.2.0-1) ...
Setting up g++-14 (14.2.0-19) ...
Setting up gcc (4:14.2.0-1) ...
Setting up g++ (4:14.2.0-1) ...
update-alternatives: using /usr/bin/g++ to provide /usr/bin/c++ (c++) in auto mode
Setting up build-essential (12.12) ...
Processing triggers for libc-bin (2.41-12) ...
 ---> Removed intermediate container 5179429fae40
 ---> ea65e2c805b9
Step 5/11 : COPY requirements.txt /tmp/requirements.txt
 ---> be1a4da96283
Step 6/11 : RUN grep -v -i '^\s*ollama' /tmp/requirements.txt | sed '/^\s*$/d' > /tmp/requirements_no_ollama.txt     && pip install --no-cache-dir -r /tmp/requirements_no_ollama.txt
 ---> Running in 9d63d49f252f
Collecting fastapi (from -r /tmp/requirements_no_ollama.txt (line 1))
  Downloading fastapi-0.117.1-py3-none-any.whl.metadata (28 kB)
Collecting uvicorn (from -r /tmp/requirements_no_ollama.txt (line 2))
  Downloading uvicorn-0.37.0-py3-none-any.whl.metadata (6.6 kB)
Collecting python-multipart (from -r /tmp/requirements_no_ollama.txt (line 3))
  Downloading python_multipart-0.0.20-py3-none-any.whl.metadata (1.8 kB)
Collecting pika (from -r /tmp/requirements_no_ollama.txt (line 4))
  Downloading pika-1.3.2-py3-none-any.whl.metadata (13 kB)
Collecting oracledb (from -r /tmp/requirements_no_ollama.txt (line 5))
  Downloading oracledb-3.3.0-cp311-cp311-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl.metadata (6.7 kB)
Collecting gradio (from -r /tmp/requirements_no_ollama.txt (line 6))
  Downloading gradio-5.47.0-py3-none-any.whl.metadata (16 kB)
Collecting psycopg2-binary (from -r /tmp/requirements_no_ollama.txt (line 7))
  Downloading psycopg2_binary-2.9.10-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl.metadata (4.9 kB)
Collecting redis (from -r /tmp/requirements_no_ollama.txt (line 8))
  Downloading redis-6.4.0-py3-none-any.whl.metadata (10 kB)
Collecting requests (from -r /tmp/requirements_no_ollama.txt (line 9))
  Downloading requests-2.32.5-py3-none-any.whl.metadata (4.9 kB)
Collecting pandas (from -r /tmp/requirements_no_ollama.txt (line 10))
  Downloading pandas-2.3.2-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl.metadata (91 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 91.2/91.2 kB 1.9 MB/s eta 0:00:00
Collecting python-dotenv (from -r /tmp/requirements_no_ollama.txt (line 11))
  Downloading python_dotenv-1.1.1-py3-none-any.whl.metadata (24 kB)
Collecting gitpython (from -r /tmp/requirements_no_ollama.txt (line 12))
  Downloading gitpython-3.1.45-py3-none-any.whl.metadata (13 kB)
Collecting mermaid-py (from -r /tmp/requirements_no_ollama.txt (line 14))
  Downloading mermaid_py-0.8.0-py3-none-any.whl.metadata (5.6 kB)
Collecting ipython (from -r /tmp/requirements_no_ollama.txt (line 15))
  Downloading ipython-9.5.0-py3-none-any.whl.metadata (4.4 kB)
Collecting sqlparse (from -r /tmp/requirements_no_ollama.txt (line 16))
  Downloading sqlparse-0.5.3-py3-none-any.whl.metadata (3.9 kB)
Collecting starlette<0.49.0,>=0.40.0 (from fastapi->-r /tmp/requirements_no_ollama.txt (line 1))
  Downloading starlette-0.48.0-py3-none-any.whl.metadata (6.3 kB)
Collecting pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0,>=1.7.4 (from fastapi->-r /tmp/requirements_no_ollama.txt (line 1))
  Downloading pydantic-2.11.9-py3-none-any.whl.metadata (68 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 68.4/68.4 kB 2.4 MB/s eta 0:00:00
Collecting typing-extensions>=4.8.0 (from fastapi->-r /tmp/requirements_no_ollama.txt (line 1))
  Downloading typing_extensions-4.15.0-py3-none-any.whl.metadata (3.3 kB)
Collecting click>=7.0 (from uvicorn->-r /tmp/requirements_no_ollama.txt (line 2))
  Downloading click-8.3.0-py3-none-any.whl.metadata (2.6 kB)
Collecting h11>=0.8 (from uvicorn->-r /tmp/requirements_no_ollama.txt (line 2))
  Downloading h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
Collecting cryptography>=3.2.1 (from oracledb->-r /tmp/requirements_no_ollama.txt (line 5))
  Downloading cryptography-46.0.1-cp311-abi3-manylinux_2_34_aarch64.whl.metadata (5.7 kB)
Collecting aiofiles<25.0,>=22.0 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading aiofiles-24.1.0-py3-none-any.whl.metadata (10 kB)
Collecting anyio<5.0,>=3.0 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading anyio-4.11.0-py3-none-any.whl.metadata (4.1 kB)
Collecting brotli>=1.1.0 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading Brotli-1.1.0-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl.metadata (5.5 kB)
Collecting ffmpy (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading ffmpy-0.6.1-py3-none-any.whl.metadata (2.9 kB)
Collecting gradio-client==1.13.2 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading gradio_client-1.13.2-py3-none-any.whl.metadata (7.1 kB)
Collecting groovy~=0.1 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading groovy-0.1.2-py3-none-any.whl.metadata (6.1 kB)
Collecting httpx<1.0,>=0.24.1 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading httpx-0.28.1-py3-none-any.whl.metadata (7.1 kB)
Collecting huggingface-hub<1.0,>=0.33.5 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading huggingface_hub-0.35.1-py3-none-any.whl.metadata (14 kB)
Collecting jinja2<4.0 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
Collecting markupsafe<4.0,>=2.0 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading MarkupSafe-3.0.2-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl.metadata (4.0 kB)
Collecting numpy<3.0,>=1.0 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading numpy-2.3.3-cp311-cp311-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl.metadata (62 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 62.1/62.1 kB 2.0 MB/s eta 0:00:00
Collecting orjson~=3.0 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading orjson-3.11.3-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl.metadata (41 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 41.9/41.9 kB 1.9 MB/s eta 0:00:00
Collecting packaging (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading packaging-25.0-py3-none-any.whl.metadata (3.3 kB)
Collecting pillow<12.0,>=8.0 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading pillow-11.3.0-cp311-cp311-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl.metadata (9.0 kB)
Collecting pydub (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading pydub-0.25.1-py2.py3-none-any.whl.metadata (1.4 kB)
Collecting pyyaml<7.0,>=5.0 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading PyYAML-6.0.2-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl.metadata (2.1 kB)
Collecting ruff>=0.9.3 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading ruff-0.13.1-py3-none-manylinux_2_17_aarch64.manylinux2014_aarch64.whl.metadata (25 kB)
Collecting safehttpx<0.2.0,>=0.1.6 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading safehttpx-0.1.6-py3-none-any.whl.metadata (4.2 kB)
Collecting semantic-version~=2.0 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading semantic_version-2.10.0-py2.py3-none-any.whl.metadata (9.7 kB)
Collecting tomlkit<0.14.0,>=0.12.0 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading tomlkit-0.13.3-py3-none-any.whl.metadata (2.8 kB)
Collecting typer<1.0,>=0.12 (from gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading typer-0.19.2-py3-none-any.whl.metadata (16 kB)
Collecting fsspec (from gradio-client==1.13.2->gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading fsspec-2025.9.0-py3-none-any.whl.metadata (10 kB)
Collecting websockets<16.0,>=13.0 (from gradio-client==1.13.2->gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading websockets-15.0.1-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl.metadata (6.8 kB)
Collecting charset_normalizer<4,>=2 (from requests->-r /tmp/requirements_no_ollama.txt (line 9))
  Downloading charset_normalizer-3.4.3-cp311-cp311-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl.metadata (36 kB)
Collecting idna<4,>=2.5 (from requests->-r /tmp/requirements_no_ollama.txt (line 9))
  Downloading idna-3.10-py3-none-any.whl.metadata (10 kB)
Collecting urllib3<3,>=1.21.1 (from requests->-r /tmp/requirements_no_ollama.txt (line 9))
  Downloading urllib3-2.5.0-py3-none-any.whl.metadata (6.5 kB)
Collecting certifi>=2017.4.17 (from requests->-r /tmp/requirements_no_ollama.txt (line 9))
  Downloading certifi-2025.8.3-py3-none-any.whl.metadata (2.4 kB)
Collecting python-dateutil>=2.8.2 (from pandas->-r /tmp/requirements_no_ollama.txt (line 10))
  Downloading python_dateutil-2.9.0.post0-py2.py3-none-any.whl.metadata (8.4 kB)
Collecting pytz>=2020.1 (from pandas->-r /tmp/requirements_no_ollama.txt (line 10))
  Downloading pytz-2025.2-py2.py3-none-any.whl.metadata (22 kB)
Collecting tzdata>=2022.7 (from pandas->-r /tmp/requirements_no_ollama.txt (line 10))
  Downloading tzdata-2025.2-py2.py3-none-any.whl.metadata (1.4 kB)
Collecting gitdb<5,>=4.0.1 (from gitpython->-r /tmp/requirements_no_ollama.txt (line 12))
  Downloading gitdb-4.0.12-py3-none-any.whl.metadata (1.2 kB)
Collecting mcp==1.10.1 (from gradio[mcp]->-r /tmp/requirements_no_ollama.txt (line 13))
  Downloading mcp-1.10.1-py3-none-any.whl.metadata (40 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 40.1/40.1 kB 3.1 MB/s eta 0:00:00
Collecting httpx-sse>=0.4 (from mcp==1.10.1->gradio[mcp]->-r /tmp/requirements_no_ollama.txt (line 13))
  Downloading httpx_sse-0.4.1-py3-none-any.whl.metadata (9.4 kB)
Collecting jsonschema>=4.20.0 (from mcp==1.10.1->gradio[mcp]->-r /tmp/requirements_no_ollama.txt (line 13))
  Downloading jsonschema-4.25.1-py3-none-any.whl.metadata (7.6 kB)
Collecting pydantic-settings>=2.5.2 (from mcp==1.10.1->gradio[mcp]->-r /tmp/requirements_no_ollama.txt (line 13))
  Downloading pydantic_settings-2.11.0-py3-none-any.whl.metadata (3.4 kB)
Collecting sse-starlette>=1.6.1 (from mcp==1.10.1->gradio[mcp]->-r /tmp/requirements_no_ollama.txt (line 13))
  Downloading sse_starlette-3.0.2-py3-none-any.whl.metadata (11 kB)
Collecting decorator (from ipython->-r /tmp/requirements_no_ollama.txt (line 15))
  Downloading decorator-5.2.1-py3-none-any.whl.metadata (3.9 kB)
Collecting ipython-pygments-lexers (from ipython->-r /tmp/requirements_no_ollama.txt (line 15))
  Downloading ipython_pygments_lexers-1.1.1-py3-none-any.whl.metadata (1.1 kB)
Collecting jedi>=0.16 (from ipython->-r /tmp/requirements_no_ollama.txt (line 15))
  Downloading jedi-0.19.2-py2.py3-none-any.whl.metadata (22 kB)
Collecting matplotlib-inline (from ipython->-r /tmp/requirements_no_ollama.txt (line 15))
  Downloading matplotlib_inline-0.1.7-py3-none-any.whl.metadata (3.9 kB)
Collecting pexpect>4.3 (from ipython->-r /tmp/requirements_no_ollama.txt (line 15))
  Downloading pexpect-4.9.0-py2.py3-none-any.whl.metadata (2.5 kB)
Collecting prompt_toolkit<3.1.0,>=3.0.41 (from ipython->-r /tmp/requirements_no_ollama.txt (line 15))
  Downloading prompt_toolkit-3.0.52-py3-none-any.whl.metadata (6.4 kB)
Collecting pygments>=2.4.0 (from ipython->-r /tmp/requirements_no_ollama.txt (line 15))
  Downloading pygments-2.19.2-py3-none-any.whl.metadata (2.5 kB)
Collecting stack_data (from ipython->-r /tmp/requirements_no_ollama.txt (line 15))
  Downloading stack_data-0.6.3-py3-none-any.whl.metadata (18 kB)
Collecting traitlets>=5.13.0 (from ipython->-r /tmp/requirements_no_ollama.txt (line 15))
  Downloading traitlets-5.14.3-py3-none-any.whl.metadata (10 kB)
Collecting sniffio>=1.1 (from anyio<5.0,>=3.0->gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading sniffio-1.3.1-py3-none-any.whl.metadata (3.9 kB)
Collecting cffi>=2.0.0 (from cryptography>=3.2.1->oracledb->-r /tmp/requirements_no_ollama.txt (line 5))
  Downloading cffi-2.0.0-cp311-cp311-manylinux2014_aarch64.manylinux_2_17_aarch64.whl.metadata (2.6 kB)
Collecting smmap<6,>=3.0.1 (from gitdb<5,>=4.0.1->gitpython->-r /tmp/requirements_no_ollama.txt (line 12))
  Downloading smmap-5.0.2-py3-none-any.whl.metadata (4.3 kB)
Collecting httpcore==1.* (from httpx<1.0,>=0.24.1->gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading httpcore-1.0.9-py3-none-any.whl.metadata (21 kB)
Collecting filelock (from huggingface-hub<1.0,>=0.33.5->gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading filelock-3.19.1-py3-none-any.whl.metadata (2.1 kB)
Collecting tqdm>=4.42.1 (from huggingface-hub<1.0,>=0.33.5->gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading tqdm-4.67.1-py3-none-any.whl.metadata (57 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 57.7/57.7 kB 2.4 MB/s eta 0:00:00
Collecting hf-xet<2.0.0,>=1.1.3 (from huggingface-hub<1.0,>=0.33.5->gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading hf_xet-1.1.10-cp37-abi3-manylinux_2_28_aarch64.whl.metadata (4.7 kB)
Collecting parso<0.9.0,>=0.8.4 (from jedi>=0.16->ipython->-r /tmp/requirements_no_ollama.txt (line 15))
  Downloading parso-0.8.5-py2.py3-none-any.whl.metadata (8.3 kB)
Collecting ptyprocess>=0.5 (from pexpect>4.3->ipython->-r /tmp/requirements_no_ollama.txt (line 15))
  Downloading ptyprocess-0.7.0-py2.py3-none-any.whl.metadata (1.3 kB)
Collecting wcwidth (from prompt_toolkit<3.1.0,>=3.0.41->ipython->-r /tmp/requirements_no_ollama.txt (line 15))
  Downloading wcwidth-0.2.14-py2.py3-none-any.whl.metadata (15 kB)
Collecting annotated-types>=0.6.0 (from pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0,>=1.7.4->fastapi->-r /tmp/requirements_no_ollama.txt (line 1))
  Downloading annotated_types-0.7.0-py3-none-any.whl.metadata (15 kB)
Collecting pydantic-core==2.33.2 (from pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0,>=1.7.4->fastapi->-r /tmp/requirements_no_ollama.txt (line 1))
  Downloading pydantic_core-2.33.2-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl.metadata (6.8 kB)
Collecting typing-inspection>=0.4.0 (from pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0,>=1.7.4->fastapi->-r /tmp/requirements_no_ollama.txt (line 1))
  Downloading typing_inspection-0.4.1-py3-none-any.whl.metadata (2.6 kB)
Collecting six>=1.5 (from python-dateutil>=2.8.2->pandas->-r /tmp/requirements_no_ollama.txt (line 10))
  Downloading six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
Collecting shellingham>=1.3.0 (from typer<1.0,>=0.12->gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading shellingham-1.5.4-py2.py3-none-any.whl.metadata (3.5 kB)
Collecting rich>=10.11.0 (from typer<1.0,>=0.12->gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading rich-14.1.0-py3-none-any.whl.metadata (18 kB)
Collecting executing>=1.2.0 (from stack_data->ipython->-r /tmp/requirements_no_ollama.txt (line 15))
  Downloading executing-2.2.1-py2.py3-none-any.whl.metadata (8.9 kB)
Collecting asttokens>=2.1.0 (from stack_data->ipython->-r /tmp/requirements_no_ollama.txt (line 15))
  Downloading asttokens-3.0.0-py3-none-any.whl.metadata (4.7 kB)
Collecting pure-eval (from stack_data->ipython->-r /tmp/requirements_no_ollama.txt (line 15))
  Downloading pure_eval-0.2.3-py3-none-any.whl.metadata (6.3 kB)
Collecting pycparser (from cffi>=2.0.0->cryptography>=3.2.1->oracledb->-r /tmp/requirements_no_ollama.txt (line 5))
  Downloading pycparser-2.23-py3-none-any.whl.metadata (993 bytes)
Collecting attrs>=22.2.0 (from jsonschema>=4.20.0->mcp==1.10.1->gradio[mcp]->-r /tmp/requirements_no_ollama.txt (line 13))
  Downloading attrs-25.3.0-py3-none-any.whl.metadata (10 kB)
Collecting jsonschema-specifications>=2023.03.6 (from jsonschema>=4.20.0->mcp==1.10.1->gradio[mcp]->-r /tmp/requirements_no_ollama.txt (line 13))
  Downloading jsonschema_specifications-2025.9.1-py3-none-any.whl.metadata (2.9 kB)
Collecting referencing>=0.28.4 (from jsonschema>=4.20.0->mcp==1.10.1->gradio[mcp]->-r /tmp/requirements_no_ollama.txt (line 13))
  Downloading referencing-0.36.2-py3-none-any.whl.metadata (2.8 kB)
Collecting rpds-py>=0.7.1 (from jsonschema>=4.20.0->mcp==1.10.1->gradio[mcp]->-r /tmp/requirements_no_ollama.txt (line 13))
  Downloading rpds_py-0.27.1-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl.metadata (4.2 kB)
Collecting markdown-it-py>=2.2.0 (from rich>=10.11.0->typer<1.0,>=0.12->gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading markdown_it_py-4.0.0-py3-none-any.whl.metadata (7.3 kB)
Collecting mdurl~=0.1 (from markdown-it-py>=2.2.0->rich>=10.11.0->typer<1.0,>=0.12->gradio->-r /tmp/requirements_no_ollama.txt (line 6))
  Downloading mdurl-0.1.2-py3-none-any.whl.metadata (1.6 kB)
Downloading fastapi-0.117.1-py3-none-any.whl (95 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 96.0/96.0 kB 2.4 MB/s eta 0:00:00
Downloading uvicorn-0.37.0-py3-none-any.whl (67 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 68.0/68.0 kB 3.1 MB/s eta 0:00:00
Downloading python_multipart-0.0.20-py3-none-any.whl (24 kB)
Downloading pika-1.3.2-py3-none-any.whl (155 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 155.4/155.4 kB 2.7 MB/s eta 0:00:00
Downloading oracledb-3.3.0-cp311-cp311-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl (2.4 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.4/2.4 MB 3.1 MB/s eta 0:00:00
Downloading gradio-5.47.0-py3-none-any.whl (60.4 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 60.4/60.4 MB 14.4 MB/s eta 0:00:00
Downloading gradio_client-1.13.2-py3-none-any.whl (325 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 325.3/325.3 kB 19.5 MB/s eta 0:00:00
Downloading psycopg2_binary-2.9.10-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (2.9 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.9/2.9 MB 16.1 MB/s eta 0:00:00
Downloading redis-6.4.0-py3-none-any.whl (279 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 279.8/279.8 kB 20.6 MB/s eta 0:00:00
Downloading requests-2.32.5-py3-none-any.whl (64 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 64.7/64.7 kB 37.2 MB/s eta 0:00:00
Downloading pandas-2.3.2-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (11.8 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 11.8/11.8 MB 14.9 MB/s eta 0:00:00
Downloading python_dotenv-1.1.1-py3-none-any.whl (20 kB)
Downloading gitpython-3.1.45-py3-none-any.whl (208 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 208.2/208.2 kB 18.7 MB/s eta 0:00:00
Downloading mcp-1.10.1-py3-none-any.whl (150 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 150.9/150.9 kB 21.7 MB/s eta 0:00:00
Downloading mermaid_py-0.8.0-py3-none-any.whl (31 kB)
Downloading ipython-9.5.0-py3-none-any.whl (612 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 612.4/612.4 kB 20.6 MB/s eta 0:00:00
Downloading sqlparse-0.5.3-py3-none-any.whl (44 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 44.4/44.4 kB 153.6 MB/s eta 0:00:00
Downloading aiofiles-24.1.0-py3-none-any.whl (15 kB)
Downloading anyio-4.11.0-py3-none-any.whl (109 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 109.1/109.1 kB 139.7 MB/s eta 0:00:00
Downloading Brotli-1.1.0-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (2.9 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.9/2.9 MB 18.0 MB/s eta 0:00:00
Downloading certifi-2025.8.3-py3-none-any.whl (161 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 161.2/161.2 kB 21.5 MB/s eta 0:00:00
Downloading charset_normalizer-3.4.3-cp311-cp311-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl (145 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 145.5/145.5 kB 30.5 MB/s eta 0:00:00
Downloading click-8.3.0-py3-none-any.whl (107 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 107.3/107.3 kB 19.7 MB/s eta 0:00:00
Downloading cryptography-46.0.1-cp311-abi3-manylinux_2_34_aarch64.whl (4.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.3/4.3 MB 19.0 MB/s eta 0:00:00
Downloading gitdb-4.0.12-py3-none-any.whl (62 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 62.8/62.8 kB 18.6 MB/s eta 0:00:00
Downloading groovy-0.1.2-py3-none-any.whl (14 kB)
Downloading h11-0.16.0-py3-none-any.whl (37 kB)
Downloading httpx-0.28.1-py3-none-any.whl (73 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 73.5/73.5 kB 57.1 MB/s eta 0:00:00
Downloading httpcore-1.0.9-py3-none-any.whl (78 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 78.8/78.8 kB 98.7 MB/s eta 0:00:00
Downloading huggingface_hub-0.35.1-py3-none-any.whl (563 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 563.3/563.3 kB 25.2 MB/s eta 0:00:00
Downloading idna-3.10-py3-none-any.whl (70 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 70.4/70.4 kB 331.0 MB/s eta 0:00:00
Downloading jedi-0.19.2-py2.py3-none-any.whl (1.6 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.6/1.6 MB 22.6 MB/s eta 0:00:00
Downloading jinja2-3.1.6-py3-none-any.whl (134 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 134.9/134.9 kB 28.5 MB/s eta 0:00:00
Downloading MarkupSafe-3.0.2-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (23 kB)
Downloading numpy-2.3.3-cp311-cp311-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl (14.6 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 14.6/14.6 MB 16.7 MB/s eta 0:00:00
Downloading orjson-3.11.3-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (123 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 123.2/123.2 kB 28.9 MB/s eta 0:00:00
Downloading packaging-25.0-py3-none-any.whl (66 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 66.5/66.5 kB 28.5 MB/s eta 0:00:00
Downloading pexpect-4.9.0-py2.py3-none-any.whl (63 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 63.8/63.8 kB 32.2 MB/s eta 0:00:00
Downloading pillow-11.3.0-cp311-cp311-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl (6.0 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.0/6.0 MB 14.8 MB/s eta 0:00:00
Downloading prompt_toolkit-3.0.52-py3-none-any.whl (391 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 391.4/391.4 kB 21.2 MB/s eta 0:00:00
Downloading pydantic-2.11.9-py3-none-any.whl (444 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 444.9/444.9 kB 22.3 MB/s eta 0:00:00
Downloading pydantic_core-2.33.2-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (1.9 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.9/1.9 MB 18.9 MB/s eta 0:00:00
Downloading pygments-2.19.2-py3-none-any.whl (1.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.2/1.2 MB 25.6 MB/s eta 0:00:00
Downloading python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 229.9/229.9 kB 30.1 MB/s eta 0:00:00
Downloading pytz-2025.2-py2.py3-none-any.whl (509 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 509.2/509.2 kB 24.9 MB/s eta 0:00:00
Downloading PyYAML-6.0.2-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (736 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 736.8/736.8 kB 21.5 MB/s eta 0:00:00
Downloading ruff-0.13.1-py3-none-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (12.4 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 12.4/12.4 MB 19.5 MB/s eta 0:00:00
Downloading safehttpx-0.1.6-py3-none-any.whl (8.7 kB)
Downloading semantic_version-2.10.0-py2.py3-none-any.whl (15 kB)
Downloading starlette-0.48.0-py3-none-any.whl (73 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 73.7/73.7 kB 56.7 MB/s eta 0:00:00
Downloading tomlkit-0.13.3-py3-none-any.whl (38 kB)
Downloading traitlets-5.14.3-py3-none-any.whl (85 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 85.4/85.4 kB 56.8 MB/s eta 0:00:00
Downloading typer-0.19.2-py3-none-any.whl (46 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 46.7/46.7 kB 311.7 MB/s eta 0:00:00
Downloading typing_extensions-4.15.0-py3-none-any.whl (44 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 44.6/44.6 kB 376.9 MB/s eta 0:00:00
Downloading tzdata-2025.2-py2.py3-none-any.whl (347 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 347.8/347.8 kB 35.4 MB/s eta 0:00:00
Downloading urllib3-2.5.0-py3-none-any.whl (129 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 129.8/129.8 kB 19.1 MB/s eta 0:00:00
Downloading decorator-5.2.1-py3-none-any.whl (9.2 kB)
Downloading ffmpy-0.6.1-py3-none-any.whl (5.5 kB)
Downloading ipython_pygments_lexers-1.1.1-py3-none-any.whl (8.1 kB)
Downloading matplotlib_inline-0.1.7-py3-none-any.whl (9.9 kB)
Downloading pydub-0.25.1-py2.py3-none-any.whl (32 kB)
Downloading stack_data-0.6.3-py3-none-any.whl (24 kB)
Downloading annotated_types-0.7.0-py3-none-any.whl (13 kB)
Downloading asttokens-3.0.0-py3-none-any.whl (26 kB)
Downloading cffi-2.0.0-cp311-cp311-manylinux2014_aarch64.manylinux_2_17_aarch64.whl (216 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 216.5/216.5 kB 33.2 MB/s eta 0:00:00
Downloading executing-2.2.1-py2.py3-none-any.whl (28 kB)
Downloading fsspec-2025.9.0-py3-none-any.whl (199 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 199.3/199.3 kB 35.6 MB/s eta 0:00:00
Downloading hf_xet-1.1.10-cp37-abi3-manylinux_2_28_aarch64.whl (3.1 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.1/3.1 MB 21.6 MB/s eta 0:00:00
Downloading httpx_sse-0.4.1-py3-none-any.whl (8.1 kB)
Downloading jsonschema-4.25.1-py3-none-any.whl (90 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 90.0/90.0 kB 32.5 MB/s eta 0:00:00
Downloading parso-0.8.5-py2.py3-none-any.whl (106 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 106.7/106.7 kB 24.9 MB/s eta 0:00:00
Downloading ptyprocess-0.7.0-py2.py3-none-any.whl (13 kB)
Downloading pydantic_settings-2.11.0-py3-none-any.whl (48 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 48.6/48.6 kB 11.5 MB/s eta 0:00:00
Downloading rich-14.1.0-py3-none-any.whl (243 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 243.4/243.4 kB 25.5 MB/s eta 0:00:00
Downloading shellingham-1.5.4-py2.py3-none-any.whl (9.8 kB)
Downloading six-1.17.0-py2.py3-none-any.whl (11 kB)
Downloading smmap-5.0.2-py3-none-any.whl (24 kB)
Downloading sniffio-1.3.1-py3-none-any.whl (10 kB)
Downloading sse_starlette-3.0.2-py3-none-any.whl (11 kB)
Downloading tqdm-4.67.1-py3-none-any.whl (78 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 78.5/78.5 kB 17.4 MB/s eta 0:00:00
Downloading typing_inspection-0.4.1-py3-none-any.whl (14 kB)
Downloading websockets-15.0.1-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (182 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 182.9/182.9 kB 64.1 MB/s eta 0:00:00
Downloading filelock-3.19.1-py3-none-any.whl (15 kB)
Downloading pure_eval-0.2.3-py3-none-any.whl (11 kB)
Downloading wcwidth-0.2.14-py2.py3-none-any.whl (37 kB)
Downloading attrs-25.3.0-py3-none-any.whl (63 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 63.8/63.8 kB 72.0 MB/s eta 0:00:00
Downloading jsonschema_specifications-2025.9.1-py3-none-any.whl (18 kB)
Downloading markdown_it_py-4.0.0-py3-none-any.whl (87 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 87.3/87.3 kB 70.0 MB/s eta 0:00:00
Downloading referencing-0.36.2-py3-none-any.whl (26 kB)
Downloading rpds_py-0.27.1-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (381 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 381.6/381.6 kB 36.1 MB/s eta 0:00:00
Downloading pycparser-2.23-py3-none-any.whl (118 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 118.1/118.1 kB 37.0 MB/s eta 0:00:00
Downloading mdurl-0.1.2-py3-none-any.whl (10.0 kB)
Installing collected packages: pytz, pydub, pure-eval, ptyprocess, brotli, websockets, wcwidth, urllib3, tzdata, typing-extensions, traitlets, tqdm, tomlkit, sqlparse, sniffio, smmap, six, shellingham, semantic-version, ruff, rpds-py, redis, pyyaml, python-multipart, python-dotenv, pygments, pycparser, psycopg2-binary, pillow, pika, pexpect, parso, packaging, orjson, numpy, mdurl, markupsafe, idna, httpx-sse, hf-xet, h11, groovy, fsspec, filelock, ffmpy, executing, decorator, click, charset_normalizer, certifi, attrs, asttokens, annotated-types, aiofiles, uvicorn, typing-inspection, stack_data, requests, referencing, python-dateutil, pydantic-core, prompt_toolkit, matplotlib-inline, markdown-it-py, jinja2, jedi, ipython-pygments-lexers, httpcore, gitdb, cffi, anyio, starlette, sse-starlette, rich, pydantic, pandas, mermaid-py, jsonschema-specifications, ipython, huggingface-hub, httpx, gitpython, cryptography, typer, safehttpx, pydantic-settings, oracledb, jsonschema, gradio-client, fastapi, mcp, gradio
Successfully installed aiofiles-24.1.0 annotated-types-0.7.0 anyio-4.11.0 asttokens-3.0.0 attrs-25.3.0 brotli-1.1.0 certifi-2025.8.3 cffi-2.0.0 charset_normalizer-3.4.3 click-8.3.0 cryptography-46.0.1 decorator-5.2.1 executing-2.2.1 fastapi-0.117.1 ffmpy-0.6.1 filelock-3.19.1 fsspec-2025.9.0 gitdb-4.0.12 gitpython-3.1.45 gradio-5.47.0 gradio-client-1.13.2 groovy-0.1.2 h11-0.16.0 hf-xet-1.1.10 httpcore-1.0.9 httpx-0.28.1 httpx-sse-0.4.1 huggingface-hub-0.35.1 idna-3.10 ipython-9.5.0 ipython-pygments-lexers-1.1.1 jedi-0.19.2 jinja2-3.1.6 jsonschema-4.25.1 jsonschema-specifications-2025.9.1 markdown-it-py-4.0.0 markupsafe-3.0.2 matplotlib-inline-0.1.7 mcp-1.10.1 mdurl-0.1.2 mermaid-py-0.8.0 numpy-2.3.3 oracledb-3.3.0 orjson-3.11.3 packaging-25.0 pandas-2.3.2 parso-0.8.5 pexpect-4.9.0 pika-1.3.2 pillow-11.3.0 prompt_toolkit-3.0.52 psycopg2-binary-2.9.10 ptyprocess-0.7.0 pure-eval-0.2.3 pycparser-2.23 pydantic-2.11.9 pydantic-core-2.33.2 pydantic-settings-2.11.0 pydub-0.25.1 pygments-2.19.2 python-dateutil-2.9.0.post0 python-dotenv-1.1.1 python-multipart-0.0.20 pytz-2025.2 pyyaml-6.0.2 redis-6.4.0 referencing-0.36.2 requests-2.32.5 rich-14.1.0 rpds-py-0.27.1 ruff-0.13.1 safehttpx-0.1.6 semantic-version-2.10.0 shellingham-1.5.4 six-1.17.0 smmap-5.0.2 sniffio-1.3.1 sqlparse-0.5.3 sse-starlette-3.0.2 stack_data-0.6.3 starlette-0.48.0 tomlkit-0.13.3 tqdm-4.67.1 traitlets-5.14.3 typer-0.19.2 typing-extensions-4.15.0 typing-inspection-0.4.1 tzdata-2025.2 urllib3-2.5.0 uvicorn-0.37.0 wcwidth-0.2.14 websockets-15.0.1
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv

[notice] A new release of pip is available: 24.0 -> 25.2
[notice] To update, run: pip install --upgrade pip
 ---> Removed intermediate container 9d63d49f252f
 ---> 3141f955b606
Step 7/11 : COPY . /app
 ---> b547fd35c6e3
Step 8/11 : RUN useradd -m appuser || true
 ---> Running in 486e58c973ca
 ---> Removed intermediate container 486e58c973ca
 ---> f472cf297c9c
Step 9/11 : USER appuser
 ---> Running in 397db13066a5
 ---> Removed intermediate container 397db13066a5
 ---> cb76914f3c9e
Step 10/11 : EXPOSE 8000
 ---> Running in afd350efce62
 ---> Removed intermediate container afd350efce62
 ---> 502f3c215a9f
Step 11/11 : CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
 ---> Running in e468a4b7058f
 ---> Removed intermediate container e468a4b7058f
 ---> 8f0575e939d1
Successfully built 8f0575e939d1
Successfully tagged spf-converter:latest
ubuntu@docker-build:~/spf-converter$ docker save spf-converter:latest | gzip > spf-converter.tar.gz
permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.47/images/get?names=spf-converter%3Alatest": dial unix /var/run/docker.sock: connect: permission denied
ubuntu@docker-build:~/spf-converter$
ubuntu@docker-build:~/spf-converter$
ubuntu@docker-build:~/spf-converter$
ubuntu@docker-build:~/spf-converter$ sudo docker save spf-converter:latest | gzip > spf-converter.tar.gz
ubuntu@docker-build:~/spf-converter$ ll
total 455924
drwxr-xr-x 13 ubuntu ubuntu      4096 Sep 24 20:37 ./
drwxr-x---  6 ubuntu ubuntu      4096 Sep 24 20:31 ../
-rw-r--r--  1 ubuntu ubuntu       649 Sep 24 20:31 .env
-rw-r--r--  1 ubuntu ubuntu       117 Sep 24 20:31 .env-bkp
-rw-r--r--  1 ubuntu ubuntu       757 Sep 24 20:31 .env.example
drwxr-xr-x  7 ubuntu ubuntu      4096 Sep 24 20:31 .git/
-rw-r--r--  1 ubuntu ubuntu      1660 Sep 24 20:31 .gitignore
drwxr-xr-x  5 ubuntu ubuntu      4096 Sep 24 20:31 .venv/
-rw-r--r--  1 ubuntu ubuntu       973 Sep 24 20:31 Dockerfile
-rw-r--r--  1 ubuntu ubuntu     10391 Sep 24 20:31 README.md
drwxr-xr-x  2 ubuntu ubuntu      4096 Sep 24 20:31 __pycache__/
drwxr-xr-x  4 ubuntu ubuntu      4096 Sep 24 20:31 api/
-rw-r--r--  1 ubuntu ubuntu     46244 Sep 24 20:31 app.py
drwxr-xr-x  2 ubuntu ubuntu      4096 Sep 24 20:31 assets/
drwxr-xr-x  2 ubuntu ubuntu      4096 Sep 24 20:31 docker/
-rw-r--r--  1 ubuntu ubuntu      1623 Sep 24 20:31 docker-compose.yml
-rwxr-xr-x  1 ubuntu ubuntu      7389 Sep 24 20:31 gini.sh*
-rw-r--r--  1 ubuntu ubuntu      3798 Sep 24 20:31 manual-setup.md
drwxr-xr-x  7 ubuntu ubuntu      4096 Sep 24 20:31 project/
-rw-r--r--  1 ubuntu ubuntu      5160 Sep 24 20:31 project-structure.md
-rw-r--r--  1 ubuntu ubuntu      1662 Sep 24 20:31 reprocess_dlq.py
-rw-r--r--  1 ubuntu ubuntu       169 Sep 24 20:31 requirements.txt
-rw-rw-r--  1 ubuntu ubuntu 466675144 Sep 24 20:39 spf-converter.tar.gz
drwxr-xr-x  2 ubuntu ubuntu      4096 Sep 24 20:31 sql-assets/
drwxr-xr-x  2 ubuntu ubuntu      4096 Sep 24 20:31 testscript/
drwxr-xr-x  3 ubuntu ubuntu      4096 Sep 24 20:31 ui/
drwxr-xr-x  2 ubuntu ubuntu      4096 Sep 24 20:31 verifier/
-rw-r--r--  1 ubuntu ubuntu     15196 Sep 24 20:31 worker.py
ubun