-- Oracle Stored Procedure Examples

-- Basic Procedures 
-- 1. Simple Hello World
CREATE OR REPLACE PROCEDURE sp_hello_world AS
BEGIN
  DBMS_OUTPUT.PUT_LINE('Hello World!');
END;
/

-- 2. Procedure to show current date
CREATE OR REPLACE PROCEDURE sp_show_date AS
BEGIN
  DBMS_OUTPUT.PUT_LINE(SYSDATE);
END;
/

-- 3. Procedure with a simple calculation
CREATE OR REPLACE PROCEDURE sp_simple_calc AS
  v_result NUMBER;
BEGIN
  v_result := 10 + 20;
  DBMS_OUTPUT.PUT_LINE('Result: ' || v_result);
END;
/

-- Procedures with Parameters
-- 4. Procedure with IN parameter
CREATE OR REPLACE PROCEDURE sp_greet_person(p_name IN VARCHAR2) AS
BEGIN
  DBMS_OUTPUT.PUT_LINE('Hello, ' || p_name);
END;
/

-- 5. Procedure with OUT parameter
CREATE OR REPLACE PROCEDURE sp_get_pi(p_pi OUT NUMBER) AS
BEGIN
  p_pi := 3.14159;
END;
/

-- 6. Procedure with IN OUT parameter
CREATE OR REPLACE PROCEDURE sp_square_number(p_num IN OUT NUMBER) AS
BEGIN
  p_num := p_num * p_num;
END;
/

-- 7. Procedure with multiple parameters
CREATE OR REPLACE PROCEDURE sp_add_numbers(p_num1 IN NUMBER, p_num2 IN NUMBER, p_sum OUT NUMBER) AS
BEGIN
  p_sum := p_num1 + p_num2;
END;
/

-- Procedures with DML
-- 8. Procedure to insert a new employee
CREATE OR REPLACE PROCEDURE sp_add_employee(p_emp_name VARCHAR2, p_salary NUMBER) AS
BEGIN
  INSERT INTO employees (employee_name, salary) VALUES (p_emp_name, p_salary);
  COMMIT;
END;
/

-- 9. Procedure to update an employee's salary
CREATE OR REPLACE PROCEDURE sp_update_salary(p_emp_id NUMBER, p_new_salary NUMBER) AS
BEGIN
  UPDATE employees SET salary = p_new_salary WHERE employee_id = p_emp_id;
  COMMIT;
END;
/

-- 10. Procedure to delete an employee
CREATE OR REPLACE PROCEDURE sp_delete_employee(p_emp_id NUMBER) AS
BEGIN
  DELETE FROM employees WHERE employee_id = p_emp_id;
  COMMIT;
END;
/

-- Procedures with Cursors
-- 11. Simple cursor to fetch employee names
CREATE OR REPLACE PROCEDURE sp_get_employee_names AS
  CURSOR c_emp IS SELECT employee_name FROM employees;
  v_emp_name employees.employee_name%TYPE;
BEGIN
  OPEN c_emp;
  LOOP
    FETCH c_emp INTO v_emp_name;
    EXIT WHEN c_emp%NOTFOUND;
    DBMS_OUTPUT.PUT_LINE(v_emp_name);
  END LOOP;
  CLOSE c_emp;
END;
/

-- 12. Cursor with parameter
CREATE OR REPLACE PROCEDURE sp_get_employees_by_dept(p_dept_id NUMBER) AS
  CURSOR c_emp IS SELECT employee_name FROM employees WHERE department_id = p_dept_id;
  v_emp_name employees.employee_name%TYPE;
BEGIN
  FOR emp_rec IN c_emp LOOP
    DBMS_OUTPUT.PUT_LINE(emp_rec.employee_name);
  END LOOP;
END;
/

-- 13. Cursor with FOR UPDATE
CREATE OR REPLACE PROCEDURE sp_increase_salary_by_dept(p_dept_id NUMBER) AS
  CURSOR c_emp IS SELECT salary FROM employees WHERE department_id = p_dept_id FOR UPDATE;
BEGIN
  FOR emp_rec IN c_emp LOOP
    UPDATE employees SET salary = emp_rec.salary * 1.10 WHERE CURRENT OF c_emp;
  END LOOP;
END;
/

-- Procedures with Functions
-- 14. Procedure calling a simple function
CREATE OR REPLACE FUNCTION fn_get_total_employees RETURN NUMBER AS
  v_total NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_total FROM employees;
  RETURN v_total;
END;
/
CREATE OR REPLACE PROCEDURE sp_show_total_employees AS
BEGIN
  DBMS_OUTPUT.PUT_LINE('Total employees: ' || fn_get_total_employees);
END;
/

-- 15. Procedure with a function that takes a parameter
CREATE OR REPLACE FUNCTION fn_get_avg_salary(p_dept_id NUMBER) RETURN NUMBER AS
  v_avg_salary NUMBER;
BEGIN
  SELECT AVG(salary) INTO v_avg_salary FROM employees WHERE department_id = p_dept_id;
  RETURN v_avg_salary;
END;
/
CREATE OR REPLACE PROCEDURE sp_show_avg_salary(p_dept_id NUMBER) AS
BEGIN
  DBMS_OUTPUT.PUT_LINE('Average salary: ' || fn_get_avg_salary(p_dept_id));
END;
/

-- Procedures with Exception Handling
-- 16. Simple exception handling
CREATE OR REPLACE PROCEDURE sp_divide_by_zero AS
  v_result NUMBER;
BEGIN
  v_result := 10 / 0;
EXCEPTION
  WHEN ZERO_DIVIDE THEN
    DBMS_OUTPUT.PUT_LINE('Cannot divide by zero!');
END;
/

-- 17. Handling NO_DATA_FOUND
CREATE OR REPLACE PROCEDURE sp_get_employee_name(p_emp_id NUMBER) AS
  v_emp_name employees.employee_name%TYPE;
BEGIN
  SELECT employee_name INTO v_emp_name FROM employees WHERE employee_id = p_emp_id;
  DBMS_OUTPUT.PUT_LINE('Employee name: ' || v_emp_name);
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    DBMS_OUTPUT.PUT_LINE('Employee not found.');
END;
/

-- 18. Handling TOO_MANY_ROWS
CREATE OR REPLACE PROCEDURE sp_get_single_employee AS
  v_emp_name employees.employee_name%TYPE;
BEGIN
  SELECT employee_name INTO v_emp_name FROM employees;
EXCEPTION
  WHEN TOO_MANY_ROWS THEN
    DBMS_OUTPUT.PUT_LINE('More than one employee found.');
END;
/

-- 19. User-defined exception
CREATE OR REPLACE PROCEDURE sp_check_salary(p_salary NUMBER) AS
  e_invalid_salary EXCEPTION;
BEGIN
  IF p_salary <= 0 THEN
    RAISE e_invalid_salary;
  END IF;
EXCEPTION
  WHEN e_invalid_salary THEN
    DBMS_OUTPUT.PUT_LINE('Salary must be greater than zero.');
END;
/

-- Procedures in Packages
-- 20. Package Specification
CREATE OR REPLACE PACKAGE pkg_employee AS
  PROCEDURE sp_add_employee(p_emp_name VARCHAR2, p_salary NUMBER);
  PROCEDURE sp_delete_employee(p_emp_id NUMBER);
  FUNCTION fn_get_total_employees RETURN NUMBER;
END pkg_employee;
/

-- 21. Package Body
CREATE OR REPLACE PACKAGE BODY pkg_employee AS
  PROCEDURE sp_add_employee(p_emp_name VARCHAR2, p_salary NUMBER) AS
  BEGIN
    INSERT INTO employees (employee_name, salary) VALUES (p_emp_name, p_salary);
    COMMIT;
  END sp_add_employee;

  PROCEDURE sp_delete_employee(p_emp_id NUMBER) AS
  BEGIN
    DELETE FROM employees WHERE employee_id = p_emp_id;
    COMMIT;
  END sp_delete_employee;

  FUNCTION fn_get_total_employees RETURN NUMBER AS
    v_total NUMBER;
  BEGIN
    SELECT COUNT(*) INTO v_total FROM employees;
    RETURN v_total;
  END fn_get_total_employees;
END pkg_employee;
/

-- Advanced Procedures
-- 22. Procedure with Autonomous Transaction
CREATE OR REPLACE PROCEDURE sp_log_error(p_error_message VARCHAR2) AS
  PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
  INSERT INTO error_log (error_message, log_date) VALUES (p_error_message, SYSDATE);
  COMMIT;
END;
/

-- 23. Procedure with Dynamic SQL
CREATE OR REPLACE PROCEDURE sp_create_table(p_table_name VARCHAR2) AS
BEGIN
  EXECUTE IMMEDIATE 'CREATE TABLE ' || p_table_name || ' (id NUMBER, name VARCHAR2(100))';
END;
/

-- 24. Procedure with Bulk Collect
CREATE OR REPLACE PROCEDURE sp_get_all_employees AS
  TYPE t_emp_names IS TABLE OF employees.employee_name%TYPE;
  v_emp_names t_emp_names;
BEGIN
  SELECT employee_name BULK COLLECT INTO v_emp_names FROM employees;
  FOR i IN 1..v_emp_names.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE(v_emp_names(i));
  END LOOP;
END;
/

-- 25. Procedure with Record Type
CREATE OR REPLACE PROCEDURE sp_get_employee_details(p_emp_id NUMBER) AS
  TYPE r_employee IS RECORD (
    name employees.employee_name%TYPE,
    salary employees.salary%TYPE
  );
  v_employee r_employee;
BEGIN
  SELECT employee_name, salary INTO v_employee FROM employees WHERE employee_id = p_emp_id;
  DBMS_OUTPUT.PUT_LINE('Name: ' || v_employee.name || ', Salary: ' || v_employee.salary);
END;
/

-- 26. Procedure with conditional logic
CREATE OR REPLACE PROCEDURE sp_check_number(p_num IN NUMBER) AS
BEGIN
  IF p_num > 0 THEN
    DBMS_OUTPUT.PUT_LINE('Positive');
  ELSIF p_num < 0 THEN
    DBMS_OUTPUT.PUT_LINE('Negative');
  ELSE
    DBMS_OUTPUT.PUT_LINE('Zero');
  END IF;
END;
/

-- 27. Procedure with a WHILE loop
CREATE OR REPLACE PROCEDURE sp_while_loop_example AS
  v_counter NUMBER := 1;
BEGIN
  WHILE v_counter <= 5 LOOP
    DBMS_OUTPUT.PUT_LINE('Counter: ' || v_counter);
    v_counter := v_counter + 1;
  END LOOP;
END;
/

-- 28. Procedure with a FOR loop
CREATE OR REPLACE PROCEDURE sp_for_loop_example AS
BEGIN
  FOR i IN 1..5 LOOP
    DBMS_OUTPUT.PUT_LINE('Iteration: ' || i);
  END LOOP;
END;
/

-- 29. Procedure with a GOTO statement
CREATE OR REPLACE PROCEDURE sp_goto_example AS
BEGIN
  GOTO second_message;
  <<first_message>>
  DBMS_OUTPUT.PUT_LINE('This will be skipped.');
  GOTO end_of_procedure;
  <<second_message>>
  DBMS_OUTPUT.PUT_LINE('This is the second message.');
  <<end_of_procedure>>
  NULL;
END;
/

-- 30. Procedure with NVL function
CREATE OR REPLACE PROCEDURE sp_nvl_example(p_input VARCHAR2) AS
BEGIN
  DBMS_OUTPUT.PUT_LINE(NVL(p_input, 'Default Value'));
END;
/

-- 31. Procedure with SYSDATE
CREATE OR REPLACE PROCEDURE sp_show_time AS
BEGIN
  DBMS_OUTPUT.PUT_LINE(TO_CHAR(SYSDATE, 'HH24:MI:SS'));
END;
/

-- 32. Procedure with CLOB data type
CREATE OR REPLACE PROCEDURE sp_process_clob(p_clob IN CLOB) AS
BEGIN
  DBMS_OUTPUT.PUT_LINE('CLOB length: ' || DBMS_LOB.getlength(p_clob));
END;
/

-- 33. Procedure with NUMBER data type
CREATE OR REPLACE PROCEDURE sp_process_number(p_num IN NUMBER) AS
BEGIN
  DBMS_OUTPUT.PUT_LINE('Number: ' || p_num);
END;
/

-- 34. Procedure with NVARCHAR2 data type
CREATE OR REPLACE PROCEDURE sp_process_nvarchar2(p_text IN NVARCHAR2) AS
BEGIN
  DBMS_OUTPUT.PUT_LINE('NVARCHAR2: ' || p_text);
END;
/

-- 35. Procedure with a simple cursor and loop
CREATE OR REPLACE PROCEDURE sp_simple_cursor_loop AS
  CURSOR c_depts IS SELECT department_name FROM departments;
BEGIN
  FOR dept_rec IN c_depts LOOP
    DBMS_OUTPUT.PUT_LINE(dept_rec.department_name);
  END LOOP;
END;
/

-- 36. Procedure with explicit cursor opening, fetching, and closing
CREATE OR REPLACE PROCEDURE sp_explicit_cursor AS
  CURSOR c_jobs IS SELECT job_title FROM jobs;
  v_job_title jobs.job_title%TYPE;
BEGIN
  OPEN c_jobs;
  LOOP
    FETCH c_jobs INTO v_job_title;
    EXIT WHEN c_jobs%NOTFOUND;
    DBMS_OUTPUT.PUT_LINE(v_job_title);
  END LOOP;
  CLOSE c_jobs;
END;
/

-- 37. Procedure with a cursor and a parameter
CREATE OR REPLACE PROCEDURE sp_get_locations_by_country(p_country_id VARCHAR2) AS
  CURSOR c_locations IS SELECT city FROM locations WHERE country_id = p_country_id;
BEGIN
  FOR loc_rec IN c_locations LOOP
    DBMS_OUTPUT.PUT_LINE(loc_rec.city);
  END LOOP;
END;
/

-- 38. Procedure with a cursor and multiple columns
CREATE OR REPLACE PROCEDURE sp_get_all_departments AS
  CURSOR c_depts IS SELECT department_id, department_name FROM departments;
  v_dept_id departments.department_id%TYPE;
  v_dept_name departments.department_name%TYPE;
BEGIN
  OPEN c_depts;
  LOOP
    FETCH c_depts INTO v_dept_id, v_dept_name;
    EXIT WHEN c_depts%NOTFOUND;
    DBMS_OUTPUT.PUT_LINE('ID: ' || v_dept_id || ', Name: ' || v_dept_name);
  END LOOP;
  CLOSE c_depts;
END;
/

-- 39. Procedure with a cursor and a record
CREATE OR REPLACE PROCEDURE sp_get_all_jobs AS
  CURSOR c_jobs IS SELECT job_id, job_title FROM jobs;
  r_job c_jobs%ROWTYPE;
BEGIN
  OPEN c_jobs;
  LOOP
    FETCH c_jobs INTO r_job;
    EXIT WHEN c_jobs%NOTFOUND;
    DBMS_OUTPUT.PUT_LINE('ID: ' || r_job.job_id || ', Title: ' || r_job.job_title);
  END LOOP;
  CLOSE c_jobs;
END;
/

-- 40. Procedure with a cursor and a FOR UPDATE clause
CREATE OR REPLACE PROCEDURE sp_update_job_titles AS
  CURSOR c_jobs IS SELECT job_title FROM jobs FOR UPDATE;
BEGIN
  FOR job_rec IN c_jobs LOOP
    UPDATE jobs SET job_title = job_rec.job_title || ' (Updated)' WHERE CURRENT OF c_jobs;
  END LOOP;
END;
/

-- 41. Procedure with a cursor and a WHERE CURRENT OF clause
CREATE OR REPLACE PROCEDURE sp_delete_jobs_by_title(p_title VARCHAR2) AS
  CURSOR c_jobs IS SELECT job_id FROM jobs WHERE job_title LIKE p_title FOR UPDATE;
BEGIN
  FOR job_rec IN c_jobs LOOP
    DELETE FROM jobs WHERE CURRENT OF c_jobs;
  END LOOP;
END;
/

-- 42. Procedure with a cursor and a subquery
CREATE OR REPLACE PROCEDURE sp_get_employees_in_usa AS
  CURSOR c_emps IS
    SELECT e.employee_name
    FROM employees e
    JOIN departments d ON e.department_id = d.department_id
    JOIN locations l ON d.location_id = l.location_id
    WHERE l.country_id = 'US';
BEGIN
  FOR emp_rec IN c_emps LOOP
    DBMS_OUTPUT.PUT_LINE(emp_rec.employee_name);
  END LOOP;
END;
/

-- 43. Procedure with a cursor and an aggregate function
CREATE OR REPLACE PROCEDURE sp_get_department_stats AS
  CURSOR c_depts IS
    SELECT d.department_name, COUNT(e.employee_id) AS num_employees
    FROM departments d
    LEFT JOIN employees e ON d.department_id = e.department_id
    GROUP BY d.department_name;
BEGIN
  FOR dept_rec IN c_depts LOOP
    DBMS_OUTPUT.PUT_LINE(dept_rec.department_name || ': ' || dept_rec.num_employees);
  END LOOP;
END;
/

-- 44. Procedure with a cursor and a join
CREATE OR REPLACE PROCEDURE sp_get_employee_department_names AS
  CURSOR c_emps IS
    SELECT e.employee_name, d.department_name
    FROM employees e
    JOIN departments d ON e.department_id = d.department_id;
BEGIN
  FOR emp_rec IN c_emps LOOP
    DBMS_OUTPUT.PUT_LINE(emp_rec.employee_name || ' - ' || emp_rec.department_name);
  END LOOP;
END;
/

-- 45. Procedure with a simple function call
CREATE OR REPLACE FUNCTION fn_get_sysdate RETURN DATE AS
BEGIN
  RETURN SYSDATE;
END;
/
CREATE OR REPLACE PROCEDURE sp_call_simple_function AS
BEGIN
  DBMS_OUTPUT.PUT_LINE(fn_get_sysdate);
END;
/

-- 46. Procedure with a function that has parameters
CREATE OR REPLACE FUNCTION fn_add(p_num1 NUMBER, p_num2 NUMBER) RETURN NUMBER AS
BEGIN
  RETURN p_num1 + p_num2;
END;
/
CREATE OR REPLACE PROCEDURE sp_call_function_with_params AS
BEGIN
  DBMS_OUTPUT.PUT_LINE(fn_add(10, 20));
END;
/

-- 47. Procedure with a function that returns a string
CREATE OR REPLACE FUNCTION fn_get_greeting(p_name VARCHAR2) RETURN VARCHAR2 AS
BEGIN
  RETURN 'Hello, ' || p_name;
END;
/
CREATE OR REPLACE PROCEDURE sp_call_string_function AS
BEGIN
  DBMS_OUTPUT.PUT_LINE(fn_get_greeting('World'));
END;
/

-- 48. Procedure with a function that returns a boolean
CREATE OR REPLACE FUNCTION fn_is_positive(p_num NUMBER) RETURN BOOLEAN AS
BEGIN
  RETURN p_num > 0;
END;
/
CREATE OR REPLACE PROCEDURE sp_call_boolean_function AS
  v_is_positive BOOLEAN;
BEGIN
  v_is_positive := fn_is_positive(10);
  IF v_is_positive THEN
    DBMS_OUTPUT.PUT_LINE('Positive');
  END IF;
END;
/

-- 49. Procedure with a function that queries a table
CREATE OR REPLACE FUNCTION fn_get_employee_count RETURN NUMBER AS
  v_count NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_count FROM employees;
  RETURN v_count;
END;
/
CREATE OR REPLACE PROCEDURE sp_call_query_function AS
BEGIN
  DBMS_OUTPUT.PUT_LINE('Employee count: ' || fn_get_employee_count);
END;
/

-- 50. Procedure with a function that has an OUT parameter
CREATE OR REPLACE FUNCTION fn_get_employee(p_emp_id NUMBER, p_emp_name OUT VARCHAR2) RETURN NUMBER AS
  v_salary NUMBER;
BEGIN
  SELECT employee_name, salary INTO p_emp_name, v_salary FROM employees WHERE employee_id = p_emp_id;
  RETURN v_salary;
END;
/
CREATE OR REPLACE PROCEDURE sp_call_function_with_out_param AS
  v_emp_name employees.employee_name%TYPE;
  v_salary NUMBER;
BEGIN
  v_salary := fn_get_employee(100, v_emp_name);
  DBMS_OUTPUT.PUT_LINE('Name: ' || v_emp_name || ', Salary: ' || v_salary);
END;
/

-- 51. Procedure with a function that has an IN OUT parameter
CREATE OR REPLACE FUNCTION fn_double_value(p_num IN OUT NUMBER) RETURN NUMBER AS
BEGIN
  p_num := p_num * 2;
  RETURN p_num;
END;
/
CREATE OR REPLACE PROCEDURE sp_call_function_with_in_out_param AS
  v_num NUMBER := 10;
BEGIN
  DBMS_OUTPUT.PUT_LINE('Original value: ' || v_num);
  v_num := fn_double_value(v_num);
  DBMS_OUTPUT.PUT_LINE('New value: ' || v_num);
END;
/

-- 52. Procedure with a function that raises an exception
CREATE OR REPLACE FUNCTION fn_divide(p_num1 NUMBER, p_num2 NUMBER) RETURN NUMBER AS
BEGIN
  IF p_num2 = 0 THEN
    RAISE ZERO_DIVIDE;
  END IF;
  RETURN p_num1 / p_num2;
END;
/
CREATE OR REPLACE PROCEDURE sp_call_function_with_exception AS
BEGIN
  DBMS_OUTPUT.PUT_LINE(fn_divide(10, 0));
EXCEPTION
  WHEN ZERO_DIVIDE THEN
    DBMS_OUTPUT.PUT_LINE('Cannot divide by zero.');
END;
/

-- 53. Procedure with a function in a package
CREATE OR REPLACE PACKAGE pkg_math AS
  FUNCTION fn_add(p_num1 NUMBER, p_num2 NUMBER) RETURN NUMBER;
  FUNCTION fn_subtract(p_num1 NUMBER, p_num2 NUMBER) RETURN NUMBER;
END pkg_math;
/
CREATE OR REPLACE PACKAGE BODY pkg_math AS
  FUNCTION fn_add(p_num1 NUMBER, p_num2 NUMBER) RETURN NUMBER AS
  BEGIN
    RETURN p_num1 + p_num2;
  END fn_add;

  FUNCTION fn_subtract(p_num1 NUMBER, p_num2 NUMBER) RETURN NUMBER AS
  BEGIN
    RETURN p_num1 - p_num2;
  END fn_subtract;
END pkg_math;
/
CREATE OR REPLACE PROCEDURE sp_call_package_function AS
BEGIN
  DBMS_OUTPUT.PUT_LINE(pkg_math.fn_add(10, 20));
END;
/

-- 54. Procedure with a private function in a package
CREATE OR REPLACE PACKAGE pkg_private_function AS
  PROCEDURE sp_public_proc;
END pkg_private_function;
/
CREATE OR REPLACE PACKAGE BODY pkg_private_function AS
  FUNCTION fn_private_function RETURN VARCHAR2 AS
  BEGIN
    RETURN 'This is a private function.';
  END fn_private_function;

  PROCEDURE sp_public_proc AS
  BEGIN
    DBMS_OUTPUT.PUT_LINE(fn_private_function);
  END sp_public_proc;
END pkg_private_function;
/
CREATE OR REPLACE PROCEDURE sp_call_private_function_proc AS
BEGIN
  pkg_private_function.sp_public_proc;
END;
/

-- 55. Procedure with a simple exception handler
CREATE OR REPLACE PROCEDURE sp_simple_exception AS
BEGIN
  RAISE NO_DATA_FOUND;
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    DBMS_OUTPUT.PUT_LINE('No data found.');
END;
/

-- 56. Procedure with multiple exception handlers
CREATE OR REPLACE PROCEDURE sp_multiple_exceptions AS
BEGIN
  IF SYSDATE > TO_DATE('2025-01-01', 'YYYY-MM-DD') THEN
    RAISE NO_DATA_FOUND;
  ELSE
    RAISE TOO_MANY_ROWS;
  END IF;
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    DBMS_OUTPUT.PUT_LINE('No data found.');
  WHEN TOO_MANY_ROWS THEN
    DBMS_OUTPUT.PUT_LINE('Too many rows.');
END;
/

-- 57. Procedure with a WHEN OTHERS exception handler
CREATE OR REPLACE PROCEDURE sp_when_others_exception AS
BEGIN
  RAISE DUP_VAL_ON_INDEX;
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    DBMS_OUTPUT.PUT_LINE('No data found.');
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('An unexpected error occurred.');
END;
/

-- 58. Procedure with a user-defined exception
CREATE OR REPLACE PROCEDURE sp_user_defined_exception AS
  e_my_exception EXCEPTION;
BEGIN
  RAISE e_my_exception;
EXCEPTION
  WHEN e_my_exception THEN
    DBMS_OUTPUT.PUT_LINE('My custom exception was raised.');
END;
/

-- 59. Procedure with PRAGMA EXCEPTION_INIT
CREATE OR REPLACE PROCEDURE sp_pragma_exception_init AS
  e_deadlock EXCEPTION;
  PRAGMA EXCEPTION_INIT(e_deadlock, -60);
BEGIN
  RAISE e_deadlock;
EXCEPTION
  WHEN e_deadlock THEN
    DBMS_OUTPUT.PUT_LINE('A deadlock occurred.');
END;
/

-- 60. Procedure with RAISE_APPLICATION_ERROR
CREATE OR REPLACE PROCEDURE sp_raise_application_error AS
BEGIN
  RAISE_APPLICATION_ERROR(-20001, 'This is a custom error message.');
END;
/

-- 61. Procedure with exception propagation
CREATE OR REPLACE PROCEDURE sp_inner_proc_with_exception AS
BEGIN
  RAISE NO_DATA_FOUND;
END;
/
CREATE OR REPLACE PROCEDURE sp_outer_proc_with_exception AS
BEGIN
  sp_inner_proc_with_exception;
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    DBMS_OUTPUT.PUT_LINE('Exception caught in outer procedure.');
END;
/

-- 62. Procedure with exception handling in a function
CREATE OR REPLACE FUNCTION fn_exception_in_function RETURN NUMBER AS
BEGIN
  RAISE ZERO_DIVIDE;
END;
/
CREATE OR REPLACE PROCEDURE sp_call_function_with_exception_handling AS
BEGIN
  DBMS_OUTPUT.PUT_LINE(fn_exception_in_function);
EXCEPTION
  WHEN ZERO_DIVIDE THEN
    DBMS_OUTPUT.PUT_LINE('Exception from function caught in procedure.');
END;
/

-- 63. Procedure with SQLCODE and SQLERRM
CREATE OR REPLACE PROCEDURE sp_sqlcode_sqlerrm AS
BEGIN
  RAISE DUP_VAL_ON_INDEX;
EXCEPTION
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('Error code: ' || SQLCODE);
    DBMS_OUTPUT.PUT_LINE('Error message: ' || SQLERRM);
END;
/

-- 64. Procedure with a package specification
CREATE OR REPLACE PACKAGE pkg_simple AS
  PROCEDURE sp_hello;
END pkg_simple;
/

-- 65. Procedure with a package body
CREATE OR REPLACE PACKAGE BODY pkg_simple AS
  PROCEDURE sp_hello AS
  BEGIN
    DBMS_OUTPUT.PUT_LINE('Hello from a package!');
  END sp_hello;
END pkg_simple;
/

-- 66. Procedure calling a package procedure
CREATE OR REPLACE PROCEDURE sp_call_package_proc AS
BEGIN
  pkg_simple.sp_hello;
END;
/

-- 67. Package with a public variable
CREATE OR REPLACE PACKAGE pkg_public_variable AS
  g_public_variable VARCHAR2(100) := 'This is a public variable.';
END pkg_public_variable;
/
CREATE OR REPLACE PROCEDURE sp_access_public_variable AS
BEGIN
  DBMS_OUTPUT.PUT_LINE(pkg_public_variable.g_public_variable);
END;
/

-- 68. Package with a private variable
CREATE OR REPLACE PACKAGE pkg_private_variable AS
  PROCEDURE sp_show_private_variable;
END pkg_private_variable;
/
CREATE OR REPLACE PACKAGE BODY pkg_private_variable AS
  g_private_variable VARCHAR2(100) := 'This is a private variable.';

  PROCEDURE sp_show_private_variable AS
  BEGIN
    DBMS_OUTPUT.PUT_LINE(g_private_variable);
  END sp_show_private_variable;
END pkg_private_variable;
/
CREATE OR REPLACE PROCEDURE sp_access_private_variable AS
BEGIN
  pkg_private_variable.sp_show_private_variable;
END;
/

-- 69. Package with overloaded procedures
CREATE OR REPLACE PACKAGE pkg_overloading AS
  PROCEDURE sp_overloaded(p_param IN NUMBER);
  PROCEDURE sp_overloaded(p_param IN VARCHAR2);
END pkg_overloading;
/
CREATE OR REPLACE PACKAGE BODY pkg_overloading AS
  PROCEDURE sp_overloaded(p_param IN NUMBER) AS
  BEGIN
    DBMS_OUTPUT.PUT_LINE('Number: ' || p_param);
  END sp_overloaded;

  PROCEDURE sp_overloaded(p_param IN VARCHAR2) AS
  BEGIN
    DBMS_OUTPUT.PUT_LINE('String: ' || p_param);
  END sp_overloaded;
END pkg_overloading;
/
CREATE OR REPLACE PROCEDURE sp_call_overloaded_proc AS
BEGIN
  pkg_overloading.sp_overloaded(123);
  pkg_overloading.sp_overloaded('abc');
END;
/

-- 70. Package with a forward declaration
CREATE OR REPLACE PACKAGE pkg_forward_declaration AS
  PROCEDURE sp_proc1;
  PROCEDURE sp_proc2;
END pkg_forward_declaration;
/
CREATE OR REPLACE PACKAGE BODY pkg_forward_declaration AS
  PROCEDURE sp_proc2; -- Forward declaration

  PROCEDURE sp_proc1 AS
  BEGIN
    sp_proc2;
  END sp_proc1;

  PROCEDURE sp_proc2 AS
  BEGIN
    DBMS_OUTPUT.PUT_LINE('This is procedure 2.');
  END sp_proc2;
END pkg_forward_declaration;
/

-- 71. Package with an initialization block
CREATE OR REPLACE PACKAGE pkg_initialization AS
  g_initialized_variable VARCHAR2(100);
END pkg_initialization;
/
CREATE OR REPLACE PACKAGE BODY pkg_initialization AS
BEGIN
  g_initialized_variable := 'This variable was initialized in the package body.';
END pkg_initialization;
/
CREATE OR REPLACE PROCEDURE sp_access_initialized_variable AS
BEGIN
  DBMS_OUTPUT.PUT_LINE(pkg_initialization.g_initialized_variable);
END;
/

-- 72. Package with a cursor
CREATE OR REPLACE PACKAGE pkg_cursor AS
  CURSOR c_depts IS SELECT department_name FROM departments;
  PROCEDURE sp_show_departments;
END pkg_cursor;
/
CREATE OR REPLACE PACKAGE BODY pkg_cursor AS
  PROCEDURE sp_show_departments AS
  BEGIN
    FOR dept_rec IN c_depts LOOP
      DBMS_OUTPUT.PUT_LINE(dept_rec.department_name);
    END LOOP;
  END sp_show_departments;
END pkg_cursor;
/

-- 73. Package with a record type
CREATE OR REPLACE PACKAGE pkg_record AS
  TYPE r_employee IS RECORD (
    name employees.employee_name%TYPE,
    salary employees.salary%TYPE
  );
  PROCEDURE sp_show_employee(p_emp_id NUMBER);
END pkg_record;
/
CREATE OR REPLACE PACKAGE BODY pkg_record AS
  PROCEDURE sp_show_employee(p_emp_id NUMBER) AS
    v_employee r_employee;
  BEGIN
    SELECT employee_name, salary INTO v_employee FROM employees WHERE employee_id = p_emp_id;
    DBMS_OUTPUT.PUT_LINE('Name: ' || v_employee.name || ', Salary: ' || v_employee.salary);
  END sp_show_employee;
END pkg_record;
/

-- 74. Procedure with an autonomous transaction
CREATE OR REPLACE PROCEDURE sp_log_action(p_action VARCHAR2) AS
  PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
  INSERT INTO action_log (action, action_date) VALUES (p_action, SYSDATE);
  COMMIT;
END;
/

-- 75. Procedure calling an autonomous transaction procedure
CREATE OR REPLACE PROCEDURE sp_main_transaction AS
BEGIN
  sp_log_action('Starting main transaction.');
  -- Main transaction logic here
  sp_log_action('Ending main transaction.');
  COMMIT;
END;
/

-- 76. Procedure with dynamic SQL to create a table
CREATE OR REPLACE PROCEDURE sp_create_temp_table AS
BEGIN
  EXECUTE IMMEDIATE 'CREATE TABLE temp_table (id NUMBER, data VARCHAR2(100))';
END;
/

-- 77. Procedure with dynamic SQL to insert data
CREATE OR REPLACE PROCEDURE sp_insert_into_temp_table(p_id NUMBER, p_data VARCHAR2) AS
BEGIN
  EXECUTE IMMEDIATE 'INSERT INTO temp_table (id, data) VALUES (:1, :2)' USING p_id, p_data;
END;
/

-- 78. Procedure with dynamic SQL to query data
CREATE OR REPLACE PROCEDURE sp_query_temp_table AS
  TYPE t_cursor IS REF CURSOR;
  c_data t_cursor;
  v_id NUMBER;
  v_data VARCHAR2(100);
BEGIN
  OPEN c_data FOR 'SELECT id, data FROM temp_table';
  LOOP
    FETCH c_data INTO v_id, v_data;
    EXIT WHEN c_data%NOTFOUND;
    DBMS_OUTPUT.PUT_LINE('ID: ' || v_id || ', Data: ' || v_data);
  END LOOP;
  CLOSE c_data;
END;
/

-- 79. Procedure with dynamic SQL and BULK COLLECT
CREATE OR REPLACE PROCEDURE sp_bulk_collect_dynamic AS
  TYPE t_ids IS TABLE OF NUMBER;
  v_ids t_ids;
BEGIN
  EXECUTE IMMEDIATE 'SELECT id FROM temp_table' BULK COLLECT INTO v_ids;
  FOR i IN 1..v_ids.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE('ID: ' || v_ids(i));
  END LOOP;
END;
/

-- 80. Procedure with DBMS_SQL package
CREATE OR REPLACE PROCEDURE sp_dbms_sql_example AS
  v_cursor INTEGER;
  v_rows INTEGER;
BEGIN
  v_cursor := DBMS_SQL.OPEN_CURSOR;
  DBMS_SQL.PARSE(v_cursor, 'SELECT * FROM employees', DBMS_SQL.NATIVE);
  v_rows := DBMS_SQL.EXECUTE(v_cursor);
  DBMS_SQL.CLOSE_CURSOR(v_cursor);
END;
/

-- 81. Procedure with a pipelined function
CREATE OR REPLACE TYPE t_number_row AS OBJECT (n NUMBER);
/
CREATE OR REPLACE TYPE t_number_table AS TABLE OF t_number_row;
/
CREATE OR REPLACE FUNCTION fn_pipelined_numbers(p_count NUMBER) RETURN t_number_table PIPELINED AS
BEGIN
  FOR i IN 1..p_count LOOP
    PIPE ROW(t_number_row(i));
  END LOOP;
  RETURN;
END;
/
CREATE OR REPLACE PROCEDURE sp_call_pipelined_function AS
BEGIN
  FOR rec IN (SELECT * FROM TABLE(fn_pipelined_numbers(5))) LOOP
    DBMS_OUTPUT.PUT_LINE(rec.n);
  END LOOP;
END;
/

-- 82. Procedure with a table function
CREATE OR REPLACE FUNCTION fn_table_function(p_count NUMBER) RETURN t_number_table AS
  v_table t_number_table := t_number_table();
BEGIN
  FOR i IN 1..p_count LOOP
    v_table.EXTEND;
    v_table(v_table.LAST) := t_number_row(i);
  END LOOP;
  RETURN v_table;
END;
/
CREATE OR REPLACE PROCEDURE sp_call_table_function AS
BEGIN
  FOR rec IN (SELECT * FROM TABLE(fn_table_function(5))) LOOP
    DBMS_OUTPUT.PUT_LINE(rec.n);
  END LOOP;
END;
/

-- 83. Procedure with a deterministic function
CREATE OR REPLACE FUNCTION fn_deterministic_add(p_num1 NUMBER, p_num2 NUMBER) RETURN NUMBER DETERMINISTIC AS
BEGIN
  RETURN p_num1 + p_num2;
END;
/
CREATE OR REPLACE PROCEDURE sp_call_deterministic_function AS
BEGIN
  DBMS_OUTPUT.PUT_LINE(fn_deterministic_add(10, 20));
END;
/

-- 84. Procedure with a result cache function
CREATE OR REPLACE FUNCTION fn_result_cache_function(p_param NUMBER) RETURN NUMBER RESULT_CACHE AS
BEGIN
  -- Expensive calculation here
  RETURN p_param * 2;
END;
/
CREATE OR REPLACE PROCEDURE sp_call_result_cache_function AS
BEGIN
  DBMS_OUTPUT.PUT_LINE(fn_result_cache_function(10));
  DBMS_OUTPUT.PUT_LINE(fn_result_cache_function(10)); -- This will be faster
END;
/

-- 85. Procedure with a collection type
CREATE OR REPLACE PROCEDURE sp_collection_example AS
  TYPE t_names IS TABLE OF VARCHAR2(100);
  v_names t_names := t_names('John', 'Jane', 'Peter');
BEGIN
  FOR i IN 1..v_names.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE(v_names(i));
  END LOOP;
END;
/

-- 86. Procedure with an associative array
CREATE OR REPLACE PROCEDURE sp_associative_array_example AS
  TYPE t_ages IS TABLE OF NUMBER INDEX BY VARCHAR2(100);
  v_ages t_ages;
BEGIN
  v_ages('John') := 30;
  v_ages('Jane') := 25;
  DBMS_OUTPUT.PUT_LINE('John is ' || v_ages('John') || ' years old.');
END;
/

-- 87. Procedure with a nested table
CREATE OR REPLACE PROCEDURE sp_nested_table_example AS
  TYPE t_numbers IS TABLE OF NUMBER;
  v_numbers t_numbers := t_numbers(1, 2, 3, 4, 5);
BEGIN
  FOR i IN 1..v_numbers.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE(v_numbers(i));
  END LOOP;
END;
/

-- 88. Procedure with a varray
CREATE OR REPLACE PROCEDURE sp_varray_example AS
  TYPE t_colors IS VARRAY(3) OF VARCHAR2(20);
  v_colors t_colors := t_colors('Red', 'Green', 'Blue');
BEGIN
  FOR i IN 1..v_colors.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE(v_colors(i));
  END LOOP;
END;
/

-- 89. Procedure with a record type
CREATE OR REPLACE PROCEDURE sp_record_example AS
  TYPE r_person IS RECORD (
    name VARCHAR2(100),
    age NUMBER
  );
  v_person r_person;
BEGIN
  v_person.name := 'John';
  v_person.age := 30;
  DBMS_OUTPUT.PUT_LINE('Name: ' || v_person.name || ', Age: ' || v_person.age);
END;
/

-- 90. Procedure with %TYPE attribute
CREATE OR REPLACE PROCEDURE sp_percent_type_example AS
  v_emp_name employees.employee_name%TYPE;
BEGIN
  SELECT employee_name INTO v_emp_name FROM employees WHERE employee_id = 100;
  DBMS_OUTPUT.PUT_LINE(v_emp_name);
END;
/

-- 91. Procedure with %ROWTYPE attribute
CREATE OR REPLACE PROCEDURE sp_percent_rowtype_example AS
  v_employee employees%ROWTYPE;
BEGIN
  SELECT * INTO v_employee FROM employees WHERE employee_id = 100;
  DBMS_OUTPUT.PUT_LINE('Name: ' || v_employee.employee_name || ', Salary: ' || v_employee.salary);
END;
/

-- 92. Procedure with a simple trigger
CREATE OR REPLACE TRIGGER trg_before_insert_employee
BEFORE INSERT ON employees
FOR EACH ROW
BEGIN
  :new.salary := :new.salary + 100;
END;
/

-- 93. Procedure with a compound trigger
CREATE OR REPLACE TRIGGER trg_compound_employee
FOR INSERT ON employees
COMPOUND TRIGGER
  BEFORE STATEMENT IS
  BEGIN
    DBMS_OUTPUT.PUT_LINE('Before statement');
  END BEFORE STATEMENT;

  BEFORE EACH ROW IS
  BEGIN
    :new.salary := :new.salary + 100;
  END BEFORE EACH ROW;

  AFTER EACH ROW IS
  BEGIN
    DBMS_OUTPUT.PUT_LINE('After each row');
  END AFTER EACH ROW;

  AFTER STATEMENT IS
  BEGIN
    DBMS_OUTPUT.PUT_LINE('After statement');
  END AFTER STATEMENT;
END trg_compound_employee;
/

-- 94. Procedure with a DDL trigger
CREATE OR REPLACE TRIGGER trg_ddl_audit
AFTER DDL ON SCHEMA
BEGIN
  INSERT INTO ddl_log (event, object_name, object_type, owner)
  VALUES (ora_sysevent, ora_dict_obj_name, ora_dict_obj_type, ora_dict_obj_owner);
END;
/

-- 95. Procedure with a database event trigger
CREATE OR REPLACE TRIGGER trg_logon
AFTER LOGON ON DATABASE
BEGIN
  INSERT INTO logon_log (username, logon_time)
  VALUES (USER, SYSDATE);
END;
/

-- 96. Procedure with a materialized view
CREATE MATERIALIZED VIEW mv_employee_summary
AS SELECT d.department_name, COUNT(e.employee_id) AS num_employees
   FROM departments d
   JOIN employees e ON d.department_id = e.department_id
   GROUP BY d.department_name;

-- 97. Procedure with a sequence
CREATE SEQUENCE seq_employee_id START WITH 207 INCREMENT BY 1;

-- 98. Procedure with a synonym
CREATE SYNONYM emp FOR employees;

-- 99. Procedure with a view
CREATE OR REPLACE VIEW v_employee_details AS
SELECT e.employee_name, d.department_name, j.job_title
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN jobs j ON e.job_id = j.job_id;

-- 100. Procedure with a hierarchical query
CREATE OR REPLACE PROCEDURE sp_hierarchical_query AS
BEGIN
  FOR rec IN (
    SELECT level, employee_name
    FROM employees
    START WITH manager_id IS NULL
    CONNECT BY PRIOR employee_id = manager_id
  ) LOOP
    DBMS_OUTPUT.PUT_LINE(LPAD(' ', (rec.level - 1) * 2) || rec.employee_name);
  END LOOP;
END;
/

-- 101. Procedure with a PIVOT query
CREATE OR REPLACE PROCEDURE sp_pivot_query AS
BEGIN
  FOR rec IN (
    SELECT *
    FROM (
      SELECT department_name, job_title
      FROM employees e
      JOIN departments d ON e.department_id = d.department_id
      JOIN jobs j ON e.job_id = j.job_id
    )
    PIVOT (
      COUNT(job_title)
      FOR job_title IN ('Programmer' AS prog, 'Accountant' AS acct)
    )
  ) LOOP
    DBMS_OUTPUT.PUT_LINE(rec.department_name || ' - Programmers: ' || rec.prog || ', Accountants: ' || rec.acct);
  END LOOP;
END;
/
