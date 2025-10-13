import requests
import time
import os
import json # Import json module

API_URL = "http://127.0.0.1:8000"

def poll_job_status(job_id):
    """Polls the job status endpoint until the job is complete."""
    while True:
        try:
            response = requests.get(f"{API_URL}/job/{job_id}")
            response.raise_for_status()
            job = response.json()
            status = job.get("status")

            if status in ["verified", "failed", "success"]:
                return job

        except requests.exceptions.RequestException as e:
            print(f"Error polling job status: {e}")
            return None
        time.sleep(1)

def test_spf_conversion_from_text():
    """Tests stored procedure conversion from a text string."""
    print("--- Running Test: Stored Procedure Conversion from Text ---")
    with open("../sql-assets/sample.sql", "r") as f:
        sql_content = f.read()

    try:
        response = requests.post(f"{API_URL}/convert", json={"sql": sql_content, "job_type": "sql"})
        response.raise_for_status()
        job_id = response.json().get("job_id")
        print(f"Job created with ID: {job_id}")

        job = poll_job_status(job_id)

        if job and job.get("status") in ["verified", "success"]:
            print("Test PASSED")
        else:
            print("Test FAILED")
            if job:
                print(f"Job status: {job.get('status')}")
                print(f"Error message: {job.get('error_message')}")

    except requests.exceptions.RequestException as e:
        print(f"Test FAILED: {e}")

def test_ddl_conversion_from_text():
    """Tests DDL conversion from a text string."""
    print("\n--- Running Test: DDL Conversion from Text ---")
    ddl_content = "CREATE TABLE users (id NUMBER, name VARCHAR2(100));"

    try:
        response = requests.post(f"{API_URL}/convert", json={"sql": ddl_content, "job_type": "sql"})
        response.raise_for_status()
        job_id = response.json().get("job_id")
        print(f"Job created with ID: {job_id}")

        job = poll_job_status(job_id)

        if job and job.get("status") in ["verified", "success"]:
            print("Test PASSED")
        else:
            print("Test FAILED")
            if job:
                print(f"Job status: {job.get('status')}")
                print(f"Error message: {job.get('error_message')}")

    except requests.exceptions.RequestException as e:
        print(f"Test FAILED: {e}")

def poll_aggregate_status(job_ids):
    """Polls the aggregate jobs endpoint until all jobs are complete."""
    while True:
        try:
            response = requests.post(f"{API_URL}/jobs/aggregate", json={"job_ids": job_ids})
            response.raise_for_status()
            result = response.json()
            status = result.get("status")

            if status == "completed":
                return result

        except requests.exceptions.RequestException as e:
            print(f"Error polling aggregate status: {e}")
            return None
        time.sleep(2)

def test_spf_conversion_from_file():
    """Tests stored procedure conversion from a file."""
    print("\n--- Running Test: Stored Procedure Conversion from File ---")
    file_path = "../sql-assets/airline_sprocs.sql"

    try:
        with open(file_path, "rb") as f:
            response = requests.post(f"{API_URL}/convert-file", files={"file": f}, data={"job_type": "sql"})
            response.raise_for_status()
            job_ids = response.json().get("job_ids")
            print(f"Jobs created with IDs: {job_ids}")

        result = poll_aggregate_status(job_ids)

        if result and result.get("status") == "completed":
            print("Test PASSED")
        else:
            print("Test FAILED")
            if result:
                print(f"Result: {result}")

    except requests.exceptions.RequestException as e:
        print(f"Test FAILED: {e}")

def test_ddl_conversion_from_file():
    """Tests DDL conversion from a file."""
    print("\n--- Running Test: DDL Conversion from File ---")
    ddl_content = "CREATE TABLE users (id NUMBER, name VARCHAR2(100));"
    file_path = "temp_ddl.sql"
    with open(file_path, "w") as f:
        f.write(ddl_content)

    try:
        with open(file_path, "rb") as f:
            response = requests.post(f"{API_URL}/convert-file", files={"file": f}, data={"job_type": "sql"})
            response.raise_for_status()
            job_ids = response.json().get("job_ids")
            print(f"Jobs created with IDs: {job_ids}")

        result = poll_aggregate_status(job_ids)

        if result and result.get("status") == "completed":
            print("Test PASSED")
        else:
            print("Test FAILED")
            if result:
                print(f"Result: {result}")

    except requests.exceptions.RequestException as e:
        print(f"Test FAILED: {e}")
    finally:
        os.remove(file_path)

def test_bulk_ddl_conversion():
    """Tests bulk DDL conversion from concatenated files."""
    print("\n--- Running Test: Bulk DDL Conversion from Files ---")
    ddl_files = ["../sql-assets/airline_schema.sql", "../sql-assets/table-dll.sql"]
    concatenated_ddl = ""
    for file_path in ddl_files:
        with open(file_path, "r") as f:
            concatenated_ddl += f.read() + "\n/\n"

    temp_file_path = "temp_bulk_ddl.sql"
    with open(temp_file_path, "w") as f:
        f.write(concatenated_ddl)

    try:
        with open(temp_file_path, "rb") as f:
            response = requests.post(f"{API_URL}/convert-file", files={"file": f}, data={"job_type": "sql"})
            response.raise_for_status()
            job_ids = response.json().get("job_ids")
            print(f"Jobs created with IDs: {job_ids}")

        result = poll_aggregate_status(job_ids)

        if result and result.get("status") == "completed":
            print("Test PASSED")
        else:
            print("Test FAILED")
            if result:
                print(f"Result: {result}")

    except requests.exceptions.RequestException as e:
        print(f"Test FAILED: {e}")
    finally:
        os.remove(temp_file_path)

def test_bulk_spf_conversion():
    """Tests bulk stored procedure conversion from concatenated files."""
    print("\n--- Running Test: Bulk Stored Procedure Conversion from Files ---")
    spf_files = ["../sql-assets/airline_sprocs.sql", "../sql-assets/oracle-sp-new.sql", "../sql-assets/oracle-sp.sql"]
    concatenated_spf = ""
    for file_path in spf_files:
        with open(file_path, "r") as f:
            concatenated_spf += f.read() + "\n/\n"

    temp_file_path = "temp_bulk_spf.sql"
    with open(temp_file_path, "w") as f:
        f.write(concatenated_spf)

    try:
        with open(temp_file_path, "rb") as f:
            response = requests.post(f"{API_URL}/convert-file", files={"file": f}, data={"job_type": "sql"})
            response.raise_for_status()
            job_ids = response.json().get("job_ids")
            print(f"Jobs created with IDs: {job_ids}")

        result = poll_aggregate_status(job_ids)

        if result and result.get("status") == "completed":
            print("Test PASSED")
        else:
            print("Test FAILED")
            if result:
                print(f"Result: {result}")

    except requests.exceptions.RequestException as e:
        print(f"Test FAILED: {e}")
    finally:
        os.remove(temp_file_path)

def test_execute_sql_file_on_postgres():
    """Tests executing an SQL file on PostgreSQL."""
    print("\n--- Running Test: Execute SQL File on PostgreSQL ---")
    sql_content = """
    DROP TABLE IF EXISTS test_table;
    CREATE TABLE test_table (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100)
    );
    INSERT INTO test_table (name) VALUES ('Test Name 1');
    INSERT INTO test_table (name) VALUES ('Test Name 2');
    """
    file_path = "temp_execute_sql.sql"
    with open(file_path, "w") as f:
        f.write(sql_content)

    # Mock PostgreSQL credentials - these need to be valid for your test environment
    pg_creds = {
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": "password",
        "dbname": "postgres"
    }
    pg_creds_json = json.dumps(pg_creds)

    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{API_URL}/execute-sql-file",
                files={"file": f},
                data={"pg_creds_json": pg_creds_json, "is_verification": "false"}
            )
            response.raise_for_status()
            job_id = response.json().get("job_id")
            print(f"SQL Execution Job created with ID: {job_id}")

        job = poll_job_status(job_id)

        if job and job.get("status") == "success":
            print("Test PASSED")
        else:
            print("Test FAILED")
            if job:
                print(f"Job status: {job.get('status')}")
                print(f"Error message: {job.get('error_message')}")

    except requests.exceptions.RequestException as e:
        print(f"Test FAILED: {e}")
    finally:
        os.remove(file_path)

if __name__ == "__main__":
    test_spf_conversion_from_text()
    test_ddl_conversion_from_text()
    test_spf_conversion_from_file()
    test_ddl_conversion_from_file()
    test_bulk_ddl_conversion()
    test_bulk_spf_conversion()
    test_execute_sql_file_on_postgres() # Add the new test here
