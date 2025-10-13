-- Comprehensive PostgreSQL University Database Schema
-- Author: Gemini AI
-- Date: 2025-09-22

-- Enable pgcrypto for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing objects to start fresh
DROP TABLE IF EXISTS grades, enrollments, students, courses, professors, departments CASCADE;
DROP FUNCTION IF EXISTS calculate_gpa(UUID);
DROP PROCEDURE IF EXISTS enroll_student(UUID, UUID);

-- Departments Table
CREATE TABLE departments (
    department_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    department_name VARCHAR(255) NOT NULL UNIQUE,
    department_head VARCHAR(255),
    building VARCHAR(100),
    budget NUMERIC(12, 2) CHECK (budget > 0),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Professors Table
CREATE TABLE professors (
    professor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(20),
    office_location VARCHAR(100),
    department_id UUID NOT NULL,
    hire_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL
);

-- Courses Table
CREATE TABLE courses (
    course_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_code VARCHAR(20) NOT NULL UNIQUE,
    course_title VARCHAR(255) NOT NULL,
    course_description TEXT,
    credits INT NOT NULL CHECK (credits > 0),
    department_id UUID NOT NULL,
    professor_id UUID,
    semester VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE,
    FOREIGN KEY (professor_id) REFERENCES professors(professor_id) ON DELETE SET NULL
);

-- Students Table
CREATE TABLE students (
    student_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    date_of_birth DATE,
    major VARCHAR(100),
    enrollment_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enrollments Table
CREATE TABLE enrollments (
    enrollment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL,
    course_id UUID NOT NULL,
    enrollment_date DATE DEFAULT NOW(),
    grade CHAR(2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

-- Grades Table (Alternative to grade in enrollments, for more detail)
CREATE TABLE grades (
    grade_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    enrollment_id UUID NOT NULL,
    grade_value NUMERIC(5, 2) NOT NULL, -- e.g., 95.5
    grade_letter VARCHAR(2) NOT NULL, -- e.g., A+, B, C-
    comments TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_professors_department_id ON professors(department_id);
CREATE INDEX idx_courses_department_id ON courses(department_id);
CREATE INDEX idx_courses_professor_id ON courses(professor_id);
CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX idx_grades_enrollment_id ON grades(enrollment_id);
CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_professors_email ON professors(email);

-- Stored Procedure to enroll a student in a course
CREATE OR REPLACE PROCEDURE enroll_student(
    p_student_id UUID,
    p_course_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check if the student and course exist
    IF NOT EXISTS (SELECT 1 FROM students WHERE student_id = p_student_id) THEN
        RAISE EXCEPTION 'Student with ID % does not exist', p_student_id;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM courses WHERE course_id = p_course_id) THEN
        RAISE EXCEPTION 'Course with ID % does not exist', p_course_id;
    END IF;

    -- Check if the student is already enrolled
    IF EXISTS (SELECT 1 FROM enrollments WHERE student_id = p_student_id AND course_id = p_course_id) THEN
        RAISE NOTICE 'Student % is already enrolled in course %', p_student_id, p_course_id;
        RETURN;
    END IF;

    -- Insert the new enrollment
    INSERT INTO enrollments (student_id, course_id)
    VALUES (p_student_id, p_course_id);

    RAISE NOTICE 'Student % successfully enrolled in course %', p_student_id, p_course_id;
END;
$$;

-- Function to calculate a student's GPA
CREATE OR REPLACE FUNCTION calculate_gpa(
    p_student_id UUID
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    total_points NUMERIC := 0;
    total_credits INT := 0;
    gpa NUMERIC := 0.0;
    enrollment_record RECORD;
    grade_points NUMERIC;
BEGIN
    -- Check if the student exists
    IF NOT EXISTS (SELECT 1 FROM students WHERE student_id = p_student_id) THEN
        RAISE EXCEPTION 'Student with ID % does not exist', p_student_id;
    END IF;

    FOR enrollment_record IN
        SELECT e.grade, c.credits
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.student_id = p_student_id AND e.grade IS NOT NULL
    LOOP
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
        END CASE;

        total_points := total_points + (grade_points * enrollment_record.credits);
        total_credits := total_credits + enrollment_record.credits;
    END LOOP;

    IF total_credits > 0 THEN
        gpa := total_points / total_credits;
    END IF;

    RETURN ROUND(gpa, 2);
END;
$$;

-- Sample Data Insertion

-- Departments
INSERT INTO departments (department_name, department_head, building, budget) VALUES
('Computer Science', 'Dr. Alan Turing', 'Building A', 500000.00),
('Mathematics', 'Dr. Ada Lovelace', 'Building B', 450000.00),
('Physics', 'Dr. Marie Curie', 'Building C', 600000.00);

-- Professors
DO $$
DECLARE
    cs_dept_id UUID := (SELECT department_id FROM departments WHERE department_name = 'Computer Science');
    math_dept_id UUID := (SELECT department_id FROM departments WHERE department_name = 'Mathematics');
BEGIN
    INSERT INTO professors (first_name, last_name, email, department_id, hire_date) VALUES
    ('John', 'Doe', 'john.doe@university.edu', cs_dept_id, '2020-08-15'),
    ('Jane', 'Smith', 'jane.smith@university.edu', math_dept_id, '2018-01-10');
END $$;

-- Students
INSERT INTO students (first_name, last_name, email, major, enrollment_date) VALUES
('Alice', 'Johnson', 'alice.j@university.edu', 'Computer Science', '2022-09-01'),
('Bob', 'Williams', 'bob.w@university.edu', 'Mathematics', '2021-09-01');

-- Courses
DO $$
DECLARE
    cs_dept_id UUID := (SELECT department_id FROM departments WHERE department_name = 'Computer Science');
    math_dept_id UUID := (SELECT department_id FROM departments WHERE department_name = 'Mathematics');
    prof_doe_id UUID := (SELECT professor_id FROM professors WHERE email = 'john.doe@university.edu');
BEGIN
    INSERT INTO courses (course_code, course_title, credits, department_id, professor_id, semester) VALUES
    ('CS101', 'Introduction to Programming', 3, cs_dept_id, prof_doe_id, 'Fall 2024'),
    ('MATH201', 'Calculus III', 4, math_dept_id, NULL, 'Fall 2024');
END $$;

-- Enroll students using the stored procedure
DO $$
DECLARE
    student_alice_id UUID := (SELECT student_id FROM students WHERE email = 'alice.j@university.edu');
    course_cs101_id UUID := (SELECT course_id FROM courses WHERE course_code = 'CS101');
BEGIN
    CALL enroll_student(student_alice_id, course_cs101_id);
END $$;

-- Update enrollment with a grade
DO $$
DECLARE
    enrollment_id_val UUID;
BEGIN
    SELECT enrollment_id INTO enrollment_id_val
    FROM enrollments e
    JOIN students s ON e.student_id = s.student_id
    JOIN courses c ON e.course_id = c.course_id
    WHERE s.email = 'alice.j@university.edu' AND c.course_code = 'CS101';

    UPDATE enrollments SET grade = 'A' WHERE enrollment_id = enrollment_id_val;

    INSERT INTO grades (enrollment_id, grade_value, grade_letter)
    VALUES (enrollment_id_val, 92.5, 'A');
END $$;

-- Verify GPA calculation
SELECT calculate_gpa((SELECT student_id FROM students WHERE email = 'alice.j@university.edu')) AS alice_gpa;

-- End of schema
