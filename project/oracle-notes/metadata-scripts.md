```
docker exec -i oracle-free sh -c 'cat > /tmp/my_recomp.sql' << EOF
SET SERVEROUTPUT ON
PROMPT Starting serial recompilation of all invalid objects...
EXECUTE UTL_RECOMP.RECOMP_SERIAL();
PROMPT Recompilation finished.
PROMPT
PROMPT Checking for any remaining invalid objects...
SELECT COUNT(*) || ' invalid objects remain.' FROM dba_objects WHERE status = 'INVALID';
EOF
```