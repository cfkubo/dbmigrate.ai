
-- Enable DBMS_OUTPUT for notices
SET SERVEROUTPUT ON;

-- IMPORTANT: The following CREATE USER and GRANT statements must be executed by a privileged user (e.g., SYS or SYSTEM).
-- Replace 'your_password_here' with a strong password.
CREATE USER university_user IDENTIFIED BY your_password_here;

GRANT CONNECT TO university_user;
GRANT RESOURCE TO university_user;
GRANT CREATE SESSION TO university_user;
GRANT CREATE TABLE TO university_user;
GRANT CREATE SEQUENCE TO university_user;
GRANT CREATE PROCEDURE TO university_user;
GRANT CREATE FUNCTION TO university_user;
GRANT CREATE TYPE TO university_user;
GRANT UNLIMITED TABLESPACE TO university_user; -- Grant UNLIMITED TABLESPACE or specify a quota on a specific tablespace

-- Set the current schema to the newly created user for subsequent DDL/DML operations
ALTER SESSION SET CURRENT_SCHEMA = university_user;

-- Drop existing objects to start fresh
-- Tables
BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE grades CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -942 THEN
         RAISE;
          END IF;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE enrollments CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -942 THEN
         RAISE;
      END IF;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE students CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -942 THEN
         RAISE;
      END IF;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE courses CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -942 THEN
         RAISE;
      END IF;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE professors CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -942 THEN
         RAISE;
      END IF;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE departments CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -942 THEN
         RAISE;
      END IF;
END;
/

-- Functions and Procedures
BEGIN
   EXECUTE IMMEDIATE 'DROP FUNCTION calculate_gpa';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -4043 THEN -- ORA-04043: object string does not exist
         RAISE;
      END IF;
END;
/

BEGIN
   EXECUTE IMMEDIATE 'DROP PROCEDURE enroll_student';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -4043 THEN
         RAISE;
      END IF;
END;
/

-- Departments Table
CREATE TABLE departments (
    department_id VARCHAR2(36) PRIMARY KEY,
    department_name VARCHAR2(255) NOT NULL UNIQUE,
    department_head VARCHAR2(255),
    building VARCHAR2(100),
    budget NUMBER(12, 2) CHECK (budget > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP
);

CREATE OR REPLACE TRIGGER trg_departments_pk
BEFORE INSERT ON departments
FOR EACH ROW
BEGIN
    :NEW.department_id := RAWTOHEX(SYS_GUID());
END;
/

-- Professors Table
CREATE TABLE professors (
    professor_id VARCHAR2(36) PRIMARY KEY,
    first_name VARCHAR2(100) NOT NULL,
    last_name VARCHAR2(100) NOT NULL,
    email VARCHAR2(255) NOT NULL UNIQUE,
    phone_number VARCHAR2(20),
    office_location VARCHAR2(100),
    department_id VARCHAR2(36) NOT NULL,
    hire_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL
);

CREATE OR REPLACE TRIGGER trg_professors_pk
BEFORE INSERT ON professors
FOR EACH ROW
BEGIN
    :NEW.professor_id := RAWTOHEX(SYS_GUID());
END;
/

-- Courses Table
CREATE TABLE courses (
    course_id VARCHAR2(36) PRIMARY KEY,
    course_code VARCHAR2(20) NOT NULL UNIQUE,
    course_title VARCHAR2(255) NOT NULL,
    course_description CLOB,
    credits NUMBER(10) NOT NULL CHECK (credits > 0),
    department_id VARCHAR2(36) NOT NULL,
    professor_id VARCHAR2(36),
    semester VARCHAR2(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE,
    FOREIGN KEY (professor_id) REFERENCES professors(professor_id) ON DELETE SET NULL
);

CREATE OR REPLACE TRIGGER trg_courses_pk
BEFORE INSERT ON courses
FOR EACH ROW
BEGIN
    :NEW.course_id := RAWTOHEX(SYS_GUID());
END;
/

-- Students Table
CREATE TABLE students (
    student_id VARCHAR2(36) PRIMARY KEY,
    first_name VARCHAR2(100) NOT NULL,
    last_name VARCHAR2(100) NOT NULL,
    email VARCHAR2(255) NOT NULL UNIQUE,
    date_of_birth DATE,
    major VARCHAR2(100),
    enrollment_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP
);

CREATE OR REPLACE TRIGGER trg_students_pk
BEFORE INSERT ON students
FOR EACH ROW
BEGIN
    :NEW.student_id := RAWTOHEX(SYS_GUID());
END;
/

-- Enrollments Table
CREATE TABLE enrollments (
    enrollment_id VARCHAR2(36) PRIMARY KEY,
    student_id VARCHAR2(36) NOT NULL,
    course_id VARCHAR2(36) NOT NULL,
    enrollment_date DATE DEFAULT SYSDATE,
    grade CHAR(2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP,
    UNIQUE (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

CREATE OR REPLACE TRIGGER trg_enrollments_pk
BEFORE INSERT ON enrollments
FOR EACH ROW
BEGIN
    :NEW.enrollment_id := RAWTOHEX(SYS_GUID());
END;
/

-- Grades Table (Alternative to grade in enrollments, for more detail)
CREATE TABLE grades (
    grade_id VARCHAR2(36) PRIMARY KEY,
    enrollment_id VARCHAR2(36) NOT NULL,
    grade_value NUMBER(5, 2) NOT NULL, -- e.g., 95.5
    grade_letter VARCHAR2(2) NOT NULL, -- e.g., A+, B, C-
    comments CLOB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id) ON DELETE CASCADE
);

CREATE OR REPLACE TRIGGER trg_grades_pk
BEFORE INSERT ON grades
FOR EACH ROW
BEGIN
    :NEW.grade_id := RAWTOHEX(SYS_GUID());
END;
/

-- Indexes for performance
CREATE INDEX idx_professors_department_id ON professors(department_id);
CREATE INDEX idx_courses_department_id ON courses(department_id);
CREATE INDEX idx_courses_professor_id ON courses(professor_id);
CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX idx_grades_enrollment_id ON grades(enrollment_id);


-- Stored Procedure to enroll a student in a course
CREATE OR REPLACE PROCEDURE enroll_student(
    p_student_id IN VARCHAR2,
    p_course_id IN VARCHAR2
)
IS
    v_count NUMBER;
BEGIN
    -- Check if the student and course exist
    SELECT COUNT(*) INTO v_count FROM students WHERE student_id = p_student_id;
    IF v_count = 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Student with ID ' || p_student_id || ' does not exist');
    END IF;

    SELECT COUNT(*) INTO v_count FROM courses WHERE course_id = p_course_id;
    IF v_count = 0 THEN
        RAISE_APPLICATION_ERROR(-20002, 'Course with ID ' || p_course_id || ' does not exist');
    END IF;

    -- Check if the student is already enrolled
    SELECT COUNT(*) INTO v_count FROM enrollments WHERE student_id = p_student_id AND course_id = p_course_id;
    IF v_count > 0 THEN
        DBMS_OUTPUT.PUT_LINE('Student ' || p_student_id || ' is already enrolled in course ' || p_course_id);
        RETURN;
    END IF;

    -- Insert the new enrollment
    INSERT INTO enrollments (student_id, course_id)
    VALUES (p_student_id, p_course_id);

    DBMS_OUTPUT.PUT_LINE('Student ' || p_student_id || ' successfully enrolled in course ' || p_course_id);
END;
/

-- Function to calculate a student's GPA
CREATE OR REPLACE FUNCTION calculate_gpa(
    p_student_id IN VARCHAR2
)
RETURN NUMBER
IS
    total_points NUMBER := 0;
    total_credits NUMBER := 0; -- Changed to NUMBER to match grade_points type
    gpa NUMBER := 0.0;
    grade_points NUMBER;

    CURSOR c_enrollments IS
        SELECT e.grade, c.credits
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.student_id = p_student_id AND e.grade IS NOT NULL;

    v_count NUMBER;
BEGIN
    -- Check if the student exists
    SELECT COUNT(*) INTO v_count FROM students WHERE student_id = p_student_id;
    IF v_count = 0 THEN
        RAISE_APPLICATION_ERROR(-20003, 'Student with ID ' || p_student_id || ' does not exist');
    END IF;

    FOR enrollment_record IN c_enrollments LOOP
        grade_points := CASE enrollment_record.grade
            WHEN 'A+' THEN 4.0
            WHEN 'A'  THEN 4.0
            WHEN 'A-' THEN 3.7
            WHEN 'B+' THEN 3.3
            WHEN 'B'  THEN 3.0
            WHEN 'B-' THEN 2.7
            WHEN 'C+' THEN 2.3
            WHEN 'C'  THEN 2.0
            WHEN 'C-' THEN 1.7
            WHEN 'D+' THEN 1.3
            WHEN 'D'  THEN 1.0
            WHEN 'F'  THEN 0.0
            ELSE 0.0
        END; -- Changed END CASE to END for Oracle

        total_points := total_points + (grade_points * enrollment_record.credits);
        total_credits := total_credits + enrollment_record.credits;
    END LOOP;

    IF total_credits > 0 THEN
        gpa := total_points / total_credits;
    END IF;

    RETURN ROUND(gpa, 2);
END;
/

-- Sample Data Insertion

-- Departments
INSERT INTO departments (department_name, department_head, building, budget) VALUES
('Computer Science', 'Dr. Alan Turing', 'Building A', 500000.00);
INSERT INTO departments (department_name, department_head, building, budget) VALUES
('Mathematics', 'Dr. Ada Lovelace', 'Building B', 450000.00);
INSERT INTO departments (department_name, department_head, building, budget) VALUES
('Physics', 'Dr. Marie Curie', 'Building C', 600000.00);

-- Professors
DECLARE
    cs_dept_id VARCHAR2(36);
    math_dept_id VARCHAR2(36);
BEGIN
    SELECT department_id INTO cs_dept_id FROM departments WHERE department_name = 'Computer Science';
    SELECT department_id INTO math_dept_id FROM departments WHERE department_name = 'Mathematics';

    INSERT INTO professors (first_name, last_name, email, department_id, hire_date) VALUES
    ('John', 'Doe', 'john.doe@university.edu', cs_dept_id, TO_DATE('2020-08-15', 'YYYY-MM-DD'));
    INSERT INTO professors (first_name, last_name, email, department_id, hire_date) VALUES
    ('Jane', 'Smith', 'jane.smith@university.edu', math_dept_id, TO_DATE('2018-01-10', 'YYYY-MM-DD'));
END;
/

-- Students
INSERT INTO students (first_name, last_name, email, major, enrollment_date) VALUES
('Alice', 'Johnson', 'alice.j@university.edu', 'Computer Science', TO_DATE('22-09-01', 'YY-MM-DD'));
INSERT INTO students (first_name, last_name, email, major, enrollment_date) VALUES
('Bob', 'Williams', 'bob.w@university.edu', 'Mathematics', TO_DATE('21-09-01', 'YY-MM-DD'));

-- Courses
DECLARE
    cs_dept_id VARCHAR2(36);
    math_dept_id VARCHAR2(36);
    prof_doe_id VARCHAR2(36);
BEGIN
    SELECT department_id INTO cs_dept_id FROM departments WHERE department_name = 'Computer Science';
    SELECT department_id INTO math_dept_id FROM departments WHERE department_name = 'Mathematics';
    SELECT professor_id INTO prof_doe_id FROM professors WHERE email = 'john.doe@university.edu';

    INSERT INTO courses (course_code, course_title, credits, department_id, professor_id, semester) VALUES
    ('CS101', 'Introduction to Programming', 3, cs_dept_id, prof_doe_id, 'Fall 2024');
    INSERT INTO courses (course_code, course_title, credits, department_id, professor_id, semester) VALUES
    ('MATH201', 'Calculus III', 4, math_dept_id, NULL, 'Fall 2024');
END;
/

-- Enroll students using the stored procedure
DECLARE
    student_alice_id VARCHAR2(36);
    course_cs101_id VARCHAR2(36);
BEGIN
    SELECT student_id INTO student_alice_id FROM students WHERE email = 'alice.j@university.edu';
    SELECT course_id INTO course_cs101_id FROM courses WHERE course_code = 'CS101';

    enroll_student(student_alice_id, course_cs101_id);
END;
/

-- Update enrollment with a grade
DECLARE
    enrollment_id_val VARCHAR2(36);
BEGIN
    SELECT e.enrollment_id INTO enrollment_id_val
    FROM enrollments e
    JOIN students s ON e.student_id = s.student_id
    JOIN courses c ON e.course_id = c.course_id
    WHERE s.email = 'alice.j@university.edu' AND c.course_code = 'CS101';

    UPDATE enrollments SET grade = 'A' WHERE enrollment_id = enrollment_id_val;

    INSERT INTO grades (enrollment_id, grade_value, grade_letter)
    VALUES (enrollment_id_val, 92.5, 'A');
END;
/

-- Verify GPA calculation
DECLARE
    alice_gpa NUMBER;
    student_alice_id VARCHAR2(36);
BEGIN
    SELECT student_id INTO student_alice_id FROM students WHERE email = 'alice.j@university.edu';
    alice_gpa := calculate_gpa(student_alice_id);
    DBMS_OUTPUT.PUT_LINE('Alice''s GPA: ' || alice_gpa);
END;
/

-- End of schema
