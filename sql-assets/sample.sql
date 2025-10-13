CREATE OR REPLACE PROCEDURE get_employee_name (
    p_employee_id IN employees.employee_id%TYPE,
    p_first_name OUT employees.first_name%TYPE
) AS
BEGIN
    SELECT first_name
    INTO p_first_name
    FROM employees
    WHERE employee_id = p_employee_id;
END;


CREATE TABLE EMPLOYEES (
    EMPLOYEE_ID NUMBER(6) PRIMARY KEY,
    FIRST_NAME VARCHAR2(20),
    LAST_NAME VARCHAR2(25) NOT NULL,
    EMAIL VARCHAR2(25) UNIQUE,
    PHONE_NUMBER VARCHAR2(20),
    HIRE_DATE DATE NOT NULL,
    JOB_ID VARCHAR2(10) NOT NULL,
    SALARY NUMBER(8,2),
    COMMISSION_PCT NUMBER(2,2),
    MANAGER_ID NUMBER(6),
    DEPARTMENT_ID NUMBER(4),
    CONSTRAINT FK_JOB FOREIGN KEY (JOB_ID) REFERENCES JOBS (JOB_ID),
    CONSTRAINT FK_MANAGER FOREIGN KEY (MANAGER_ID) REFERENCES EMPLOYEES (EMPLOYEE_ID),
    CONSTRAINT FK_DEPARTMENT FOREIGN KEY (DEPARTMENT_ID) REFERENCES DEPARTMENTS (DEPARTMENT_ID)
);



CREATE OR REPLACE PROCEDURE add_employee (
    p_employee_id   IN NUMBER,
    p_first_name    IN VARCHAR2,
    p_last_name     IN VARCHAR2,
    p_email         IN VARCHAR2,
    p_phone_number  IN VARCHAR2,
    p_hire_date     IN DATE,
    p_job_id        IN VARCHAR2,
    p_salary        IN NUMBER,
    p_commission_pct IN NUMBER DEFAULT NULL,
    p_manager_id    IN NUMBER DEFAULT NULL,
    p_department_id IN NUMBER DEFAULT NULL
)
AS
BEGIN
    INSERT INTO employees (
        employee_id,
        first_name,
        last_name,
        email,
        phone_number,
        hire_date,
        job_id,
        salary,
        commission_pct,
        manager_id,
        department_id
    ) VALUES (
        p_employee_id,
        p_first_name,
        p_last_name,
        p_email,
        p_phone_number,
        p_hire_date,
        p_job_id,
        p_salary,
        p_commission_pct,
        p_manager_id,
        p_department_id
    );

    COMMIT; -- Commits the transaction to make the changes permanent

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK; -- Rolls back the transaction in case of an error
        DBMS_OUTPUT.PUT_LINE('Error adding employee: ' || SQLERRM);
        RAISE; -- Re-raises the exception to propagate it to the caller
END add_employee;
/
