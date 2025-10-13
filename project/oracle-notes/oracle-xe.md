docker exec oracle-free lsnrctl status

LSNRCTL for Linux: Version 21.0.0.0.0 - Production on 21-SEP-2025 17:08:44

Copyright (c) 1991, 2021, Oracle.  All rights reserved.

Connecting to (DESCRIPTION=(ADDRESS=(PROTOCOL=IPC)(KEY=EXTPROC_FOR_XE)))
STATUS of the LISTENER
------------------------
Alias                     LISTENER
Version                   TNSLSNR for Linux: Version 21.0.0.0.0 - Production
Start Date                21-SEP-2025 16:12:19
Uptime                    0 days 0 hr. 56 min. 25 sec
Trace Level               off
Security                  ON: Local OS Authentication
SNMP                      OFF
Default Service           XE
Listener Parameter File   /opt/oracle/homes/OraDBHome21cXE/network/admin/listener.ora
Listener Log File         /opt/oracle/diag/tnslsnr/30110b4819b8/listener/alert/log.xml
Listening Endpoints Summary...
  (DESCRIPTION=(ADDRESS=(PROTOCOL=ipc)(KEY=EXTPROC_FOR_XE)))
  (DESCRIPTION=(ADDRESS=(PROTOCOL=tcp)(HOST=0.0.0.0)(PORT=1521)))
  (DESCRIPTION=(ADDRESS=(PROTOCOL=tcps)(HOST=30110b4819b8)(PORT=5500))(Security=(my_wallet_directory=/opt/oracle/admin/XE/xdb_wallet))(Presentation=HTTP)(Session=RAW))
Services Summary...
Service "234d00c564120b31e0630f02000ae5f6" has 1 instance(s).
  Instance "XE", status READY, has 1 handler(s) for this service...
Service "FREE" has 1 instance(s).
  Instance "XE", status READY, has 1 handler(s) for this service...
Service "XE" has 1 instance(s).
  Instance "XE", status READY, has 1 handler(s) for this service...
Service "freepdb1" has 1 instance(s).
  Instance "XE", status READY, has 1 handler(s) for this service...
Service "xepdb1" has 1 instance(s).
  Instance "XE", status READY, has 1 handler(s) for this service...
The command completed successfully
(base) avannala@Q2HWTCX6H4 spf-converter %