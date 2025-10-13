-- Stored Procedure 1
CREATE OR REPLACE PROCEDURE sp_test1 AS
BEGIN
  DBMS_OUTPUT.PUT_LINE('Test 1');
END;
/

-- Stored Procedure 2
CREATE OR REPLACE PROCEDURE sp_test2 AS
BEGIN
  DBMS_OUTPUT.PUT_LINE('Test 2');
END;
/

-- DDL 1
CREATE TABLE test_table1 (
  id NUMBER PRIMARY KEY,
  name VARCHAR2(100)
);
/

-- DDL 2
CREATE TABLE test_table2 (
  id NUMBER PRIMARY KEY,
  description VARCHAR2(255)
);
/