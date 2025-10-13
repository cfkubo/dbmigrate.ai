docker exec -it oracle-free sqlplus sys/password as sysdba @/scripts/co_install.sql

#####

docker exec -it oracle-free sqlplus sys/password as sysdba

SQL*Plus: Release 21.0.0.0.0 - Production on Fri Sep 26 13:52:08 2025
Version 21.3.0.0.0

Copyright (c) 1982, 2021, Oracle.  All rights reserved.


Connected to:
Oracle Database 21c Express Edition Release 21.0.0.0.0 - Production
Version 21.3.0.0.0

SQL> CREATE USER MIGRATOR IDENTIFIED BY password;

User created.

SQL> GRANT DBA TO MIGRATOR;

Grant succeeded.

SQL>

#######


(base) avannala@Q2HWTCX6H4 spf-converter % docker exec -it oracle-free sqlplus sys/password as sysdba

SQL*Plus: Release 23.0.0.0.0 - Production on Sun Sep 21 14:38:22 2025
Version 23.9.0.25.07

Copyright (c) 1982, 2025, Oracle.  All rights reserved.


Connected to:
Oracle Database 23ai Free Release 23.0.0.0.0 - Develop, Learn, and Run for Free
Version 23.9.0.25.07

SQL>
SQL>
SQL>
SQL> CREATE USER MIGRATOR IDENTIFIED BY password;
CREATE USER MIGRATOR IDENTIFIED BY password
            *
ERROR at line 1:
ORA-65096: common user or role name must start with prefix C##
Help: https://docs.oracle.com/error-help/db/ora-65096/


SQL> CREATE USER migrator IDENTIFIED BY password;
CREATE USER migrator IDENTIFIED BY password
            *
ERROR at line 1:
ORA-65096: common user or role name must start with prefix C##
Help: https://docs.oracle.com/error-help/db/ora-65096/


SQL> SHOW CON_NAME;

CON_NAME
------------------------------
CDB$ROOT
SQL> ALTER SESSION SET CONTAINER = FREEPDB1;

Session altered.

SQL> CREATE USER migrator IDENTIFIED BY password;

User created.

SQL> GRANT CREATE SESSION TO migrator;

Grant succeeded.

SQL> GRANT SELECT ANY DICTIONARY TO migrator;

Grant succeeded.

SQL> GRANT SELECT ON DBA_OBJECTS TO migrator;

Grant succeeded.

SQL> GRANT SELECT ON DBA_USERS TO migrator;

Grant succeeded.

SQL> SELECT DBMS_METADATA.GET_DDL('TABLE', 'AIRCRAFT', 'DEMOARUL') FROM DUAL;
ERROR:
ORA-00600: internal error code, arguments: [17287], [0xFFFF8C44B5F0],
[0x076758270], [], [SYS], [DBMS_METADATA], [11], [1], [], [], [], []
Help: https://docs.oracle.com/error-help/db/ora-00600/



no rows selected

SQL> SET LONG 2000000
SQL> SET PAGESIZE 0
SQL> SELECT DBMS_METADATA.GET_DDL('TABLE', 'AIRCRAFT', 'DEMOARUL') FROM DUAL;
ERROR:
ORA-00600: internal error code, arguments: [17286], [0xFFFF8C44B5F0],
[0x076758270], [], [SYS], [DBMS_METADATA], [11], [1], [], [], [], []
Help: https://docs.oracle.com/error-help/db/ora-00600/



no rows selected

SQL>     SELECT USER FROM DUAL;
SYS

SQL>
SQL>
SQL>
SQL>     SELECT owner, object_name, object_type, status
    FROM dba_objects
    WHERE owner = 'SYS' AND object_name = 'DBMS_METADATA';  2    3
SYS
DBMS_METADATA
PACKAGE 		VALID

SYS
DBMS_METADATA
PACKAGE BODY		VALID


SQL>     ALTER PACKAGE SYS.DBMS_METADATA COMPILE;
    ALTER PACKAGE SYS.DBMS_METADATA COMPILE BODY;

Package altered.

SQL>     ALTER PACKAGE SYS.DBMS_METADATA COMPILE BODY
*
ERROR at line 1:
ORA-65040: Operation is not allowed from within a pluggable database.
Help: https://docs.oracle.com/error-help/db/ora-65040/


SQL>     SELECT owner, object_name, object_type, status
    FROM dba_objects
    WHERE owner = 'SYS' AND status != 'VALID';  2    3

no rows selected

SQL> ALTER SESSION SET CONTAINER = CDB$ROOT;

Session altered.

SQL> ALTER PACKAGE SYS.DBMS_METADATA COMPILE BODY;

Warning: Package Body altered with compilation errors.

SQL> SELECT *
FROM dba_errors
WHERE owner = 'SYS' AND name = 'DBMS_METADATA' AND type = 'PACKAGE BODY';  2    3
SYS
DBMS_METADATA
PACKAGE BODY		     1	     4881	  20
PL/SQL: ORA-04063: view "SYS.KU$_XMLSCHEMA_VIEW" has errors
ERROR		       0

SYS
DBMS_METADATA
PACKAGE BODY		     2	     4879	   9
PL/SQL: SQL Statement ignored
ERROR		       0


SQL> ALTER VIEW SYS.KU$_XMLSCHEMA_VIEW COMPILE;

Warning: View altered with compilation errors.

SQL>
SQL>
