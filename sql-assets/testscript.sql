SELECT object_name, object_type, owner
FROM dba_objects
WHERE owner = 'DEMOARUL'
ORDER BY object_type, object_name;

SET LONG 2000000
SET PAGESIZE 0
SELECT DBMS_METADATA.GET_DDL('TABLE', 'AIRCRAFT', 'DEMOARUL') FROM DUAL;


