
SET SERVEROUTPUT ON;

-- Anonymous PL/SQL block to generate sample data
DECLARE
    -- Department data
    TYPE department_names_array IS VARRAY(8) OF VARCHAR2(255);
    v_department_names department_names_array := department_names_array('Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'Biology', 'History', 'Literature', 'Engineering');
    TYPE building_names_array IS VARRAY(5) OF VARCHAR2(100);
    v_building_names building_names_array := building_names_array('Building A', 'Building B', 'Building C', 'Main Hall', 'Science Wing');
    
    -- Professor data
    TYPE first_names_array IS VARRAY(10) OF VARCHAR2(100);
    v_first_names first_names_array := first_names_array('John', 'Jane', 'Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Heidi');
    TYPE last_names_array IS VARRAY(10) OF VARCHAR2(100);
    v_last_names last_names_array := last_names_array('Doe', 'Smith', 'Johnson', 'Williams', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor');
    TYPE office_locations_array IS VARRAY(5) OF VARCHAR2(100);
    v_office_locations office_locations_array := office_locations_array('A101', 'A102', 'B205', 'C310', 'D401');

    -- Student data
    TYPE major_names_array IS VARRAY(6) OF VARCHAR2(100);
    v_major_names major_names_array := major_names_array('Computer Science', 'Mathematics', 'Physics', 'Biology', 'History', 'English');

    -- Course data
    TYPE course_titles_array IS VARRAY(10) OF VARCHAR2(255);
    v_course_titles course_titles_array := course_titles_array(
        'Introduction to Programming', 'Calculus I', 'Quantum Mechanics', 'Organic Chemistry',
        'Cell Biology', 'World History', 'Shakespearean Literature', 'Software Engineering',
        'Linear Algebra', 'Thermodynamics'
    );
    TYPE semester_names_array IS VARRAY(3) OF VARCHAR2(50);
    v_semester_names semester_names_array := semester_names_array('Fall 2024', 'Spring 2025', 'Summer 2025');

    -- Grade data
    TYPE grade_letters_array IS VARRAY(6) OF VARCHAR2(2);
    v_grade_letters grade_letters_array := grade_letters_array('A', 'B', 'C', 'D', 'F', 'P'); -- P for Pass, if applicable

    -- Variables to store generated IDs
    v_department_ids SYS.ODCIVARCHAR2LIST;
    v_professor_ids SYS.ODCIVARCHAR2LIST;
    v_student_ids SYS.ODCIVARCHAR2LIST;
    v_course_ids SYS.ODCIVARCHAR2LIST;
    v_enrollment_ids SYS.ODCIVARCHAR2LIST;

    v_random_dept_id VARCHAR2(36);
    v_random_prof_id VARCHAR2(36);
    v_random_student_id VARCHAR2(36);
    v_random_course_id VARCHAR2(36);
    v_random_enrollment_id VARCHAR2(36);

    v_first_name VARCHAR2(100);
    v_last_name VARCHAR2(100);
    v_email VARCHAR2(255);
    v_phone_number VARCHAR2(20);
    v_hire_date DATE;
    v_date_of_birth DATE;
    v_enrollment_date DATE;
    v_course_code VARCHAR2(20);
    v_credits NUMBER;
    v_grade_value NUMBER(5,2);
    v_grade_letter VARCHAR2(2);

BEGIN
    DBMS_OUTPUT.PUT_LINE('--- Generating Sample Data ---');

    -- Clear existing data (optional, if running multiple times)
    -- DELETE FROM grades;
    -- DELETE FROM enrollments;
    -- DELETE FROM courses;
    -- DELETE FROM professors;
    -- DELETE FROM students;
    -- DELETE FROM departments;

    -- 1. Insert Departments
    DBMS_OUTPUT.PUT_LINE('Inserting Departments...');
    FOR i IN 1..v_department_names.COUNT LOOP
        INSERT INTO departments (department_id, department_name, department_head, building, budget, created_at, updated_at)
        VALUES (RAWTOHEX(SYS_GUID()),
                v_department_names(i),
                v_first_names(TRUNC(DBMS_RANDOM.VALUE(1, v_first_names.COUNT + 1))) || ' ' || v_last_names(TRUNC(DBMS_RANDOM.VALUE(1, v_last_names.COUNT + 1))),
                v_building_names(TRUNC(DBMS_RANDOM.VALUE(1, v_building_names.COUNT + 1))),
                TRUNC(DBMS_RANDOM.VALUE(100000, 1000000), 2),
                SYSTIMESTAMP,
                SYSTIMESTAMP);
    END LOOP;
    SELECT department_id BULK COLLECT INTO v_department_ids FROM departments;
    DBMS_OUTPUT.PUT_LINE(v_department_ids.COUNT || ' Departments inserted.');

    -- 2. Insert Professors
    DBMS_OUTPUT.PUT_LINE('Inserting Professors...');
    FOR i IN 1..20 LOOP -- Insert 20 professors
        v_first_name := v_first_names(TRUNC(DBMS_RANDOM.VALUE(1, v_first_names.COUNT + 1)));
        v_last_name := v_last_names(TRUNC(DBMS_RANDOM.VALUE(1, v_last_names.COUNT + 1)));
        v_email := LOWER(v_first_name || '.' || v_last_name || i || '@university.edu'); -- Add i for uniqueness
        v_phone_number := TO_CHAR(TRUNC(DBMS_RANDOM.VALUE(1000000000, 9999999999)));
        v_random_dept_id := v_department_ids(TRUNC(DBMS_RANDOM.VALUE(1, v_department_ids.COUNT + 1)));
        v_hire_date := TRUNC(SYSDATE - DBMS_RANDOM.VALUE(365, 365*20));

        INSERT INTO professors (professor_id, first_name, last_name, email, phone_number, office_location, department_id, hire_date, created_at, updated_at)
        VALUES (RAWTOHEX(SYS_GUID()),
                v_first_name,
                v_last_name,
                v_email,
                v_phone_number,
                v_office_locations(TRUNC(DBMS_RANDOM.VALUE(1, v_office_locations.COUNT + 1))),
                v_random_dept_id,
                v_hire_date,
                SYSTIMESTAMP,
                SYSTIMESTAMP);
    END LOOP;
    SELECT professor_id BULK COLLECT INTO v_professor_ids FROM professors;
    DBMS_OUTPUT.PUT_LINE(v_professor_ids.COUNT || ' Professors inserted.');

    -- 3. Insert Students
    DBMS_OUTPUT.PUT_LINE('Inserting Students...');
    FOR i IN 1..50 LOOP -- Insert 50 students
        v_first_name := v_first_names(TRUNC(DBMS_RANDOM.VALUE(1, v_first_names.COUNT + 1)));
        v_last_name := v_last_names(TRUNC(DBMS_RANDOM.VALUE(1, v_last_names.COUNT + 1)));
        v_email := LOWER(v_first_name || '.' || v_last_name || i || '@student.university.edu'); -- Add i for uniqueness
        v_date_of_birth := TRUNC(SYSDATE - DBMS_RANDOM.VALUE(365*18, 365*25));
        v_enrollment_date := TRUNC(SYSDATE - DBMS_RANDOM.VALUE(0, 365*4));

        INSERT INTO students (student_id, first_name, last_name, email, date_of_birth, major, enrollment_date, created_at, updated_at)
        VALUES (RAWTOHEX(SYS_GUID()),
                v_first_name,
                v_last_name,
                v_email,
                v_date_of_birth,
                v_major_names(TRUNC(DBMS_RANDOM.VALUE(1, v_major_names.COUNT + 1))),
                v_enrollment_date,
                SYSTIMESTAMP,
                SYSTIMESTAMP);
    END LOOP;
    SELECT student_id BULK COLLECT INTO v_student_ids FROM students;
    DBMS_OUTPUT.PUT_LINE(v_student_ids.COUNT || ' Students inserted.');

    -- 4. Insert Courses
    DBMS_OUTPUT.PUT_LINE('Inserting Courses...');
    FOR i IN 1..30 LOOP -- Insert 30 courses
        v_random_dept_id := v_department_ids(TRUNC(DBMS_RANDOM.VALUE(1, v_department_ids.COUNT + 1)));
        v_random_prof_id := NULL;
        IF DBMS_RANDOM.VALUE(0,1) > 0.2 THEN -- 80% chance of having a professor
            v_random_prof_id := v_professor_ids(TRUNC(DBMS_RANDOM.VALUE(1, v_professor_ids.COUNT + 1)));
        END IF;
        v_credits := TRUNC(DBMS_RANDOM.VALUE(1, 5));
        v_course_code := UPPER(SUBSTR(v_department_names(TRUNC(DBMS_RANDOM.VALUE(1, v_department_names.COUNT + 1))), 1, 2)) || TRUNC(DBMS_RANDOM.VALUE(100, 499));

        INSERT INTO courses (course_id, course_code, course_title, course_description, credits, department_id, professor_id, semester, created_at, updated_at)
        VALUES (RAWTOHEX(SYS_GUID()),
                v_course_code,
                v_course_titles(TRUNC(DBMS_RANDOM.VALUE(1, v_course_titles.COUNT + 1))),
                'Description for ' || v_course_code || ' course.',
                v_credits,
                v_random_dept_id,
                v_random_prof_id,
                v_semester_names(TRUNC(DBMS_RANDOM.VALUE(1, v_semester_names.COUNT + 1))),
                SYSTIMESTAMP,
                SYSTIMESTAMP);
    END LOOP;
    SELECT course_id BULK COLLECT INTO v_course_ids FROM courses;
    DBMS_OUTPUT.PUT_LINE(v_course_ids.COUNT || ' Courses inserted.');

    -- 5. Insert Enrollments
    DBMS_OUTPUT.PUT_LINE('Inserting Enrollments...');
    FOR i IN 1..100 LOOP -- Insert 100 enrollments
        v_random_student_id := v_student_ids(TRUNC(DBMS_RANDOM.VALUE(1, v_student_ids.COUNT + 1)));
        v_random_course_id := v_course_ids(TRUNC(DBMS_RANDOM.VALUE(1, v_course_ids.COUNT + 1)));
        v_enrollment_date := TRUNC(SYSDATE - DBMS_RANDOM.VALUE(0, 365*2));
        v_grade_letter := NULL;
        IF DBMS_RANDOM.VALUE(0,1) > 0.1 THEN -- 90% chance of having a grade
            v_grade_letter := v_grade_letters(TRUNC(DBMS_RANDOM.VALUE(1, v_grade_letters.COUNT + 1)));
        END IF;

        BEGIN
            INSERT INTO enrollments (enrollment_id, student_id, course_id, enrollment_date, grade, created_at, updated_at)
            VALUES (RAWTOHEX(SYS_GUID()),
                    v_random_student_id,
                    v_random_course_id,
                    v_enrollment_date,
                    v_grade_letter,
                    SYSTIMESTAMP,
                    SYSTIMESTAMP);
        EXCEPTION
            WHEN DUP_VAL_ON_INDEX THEN
                NULL; -- Ignore duplicate enrollments (student_id, course_id unique constraint)
        END;
    END LOOP;
    SELECT enrollment_id BULK COLLECT INTO v_enrollment_ids FROM enrollments;
    DBMS_OUTPUT.PUT_LINE(v_enrollment_ids.COUNT || ' Enrollments inserted (duplicates ignored).');

    -- 6. Insert Grades
    DBMS_OUTPUT.PUT_LINE('Inserting Grades...');
    FOR i IN 1..v_enrollment_ids.COUNT LOOP -- Insert grades for existing enrollments
        v_random_enrollment_id := v_enrollment_ids(i);
        v_grade_value := TRUNC(DBMS_RANDOM.VALUE(50, 100), 2);
        
        -- Determine grade letter based on value (simplified)
        IF v_grade_value >= 90 THEN v_grade_letter := 'A';
        ELSIF v_grade_value >= 80 THEN v_grade_letter := 'B';
        ELSIF v_grade_value >= 70 THEN v_grade_letter := 'C';
        ELSIF v_grade_value >= 60 THEN v_grade_letter := 'D';
        ELSE v_grade_letter := 'F';
        END IF;

        BEGIN
            INSERT INTO grades (grade_id, enrollment_id, grade_value, grade_letter, comments, created_at, updated_at)
            VALUES (RAWTOHEX(SYS_GUID()),
                    v_random_enrollment_id,
                    v_grade_value,
                    v_grade_letter,
                    'Randomly generated grade.',
                    SYSTIMESTAMP,
                    SYSTIMESTAMP);
        EXCEPTION
            WHEN DUP_VAL_ON_INDEX THEN
                NULL; -- Ignore if a grade for this enrollment already exists (though not explicitly constrained, good practice)
        END;
    END LOOP;
    DBMS_OUTPUT.PUT_LINE(v_enrollment_ids.COUNT || ' Grades attempted (some might be duplicates or for enrollments without grades).');

    DBMS_OUTPUT.PUT_LINE('--- Sample Data Generation Complete ---');

    COMMIT; -- Commit all changes
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK; -- Rollback in case of any error
        DBMS_OUTPUT.PUT_LINE('Error generating sample data: ' || SQLERRM);
END;
/
