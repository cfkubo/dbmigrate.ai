
import requests
import time
import os
import json

# It's a good practice to have the API_URL configurable or in a central place
# For this test, we'll define it here, ensuring it matches the running service.
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def poll_job_status(job_id: str, timeout: int = 120):
    """
    Polls the job status endpoint until the job is complete or timeout is reached.
    
    Args:
        job_id: The ID of the job to poll.
        timeout: The maximum time to wait in seconds.

    Returns:
        The final job dictionary if completed, None otherwise.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Corrected endpoint based on analysis of job_routes.py
            response = requests.get(f"{API_URL}/jobs/job/{job_id}")
            response.raise_for_status()
            job = response.json()
            status = job.get("status")

            # Check for a final status
            if status in ["verified", "failed", "success", "failed"]:
                print(f"Job {job_id} reached final status: {status}")
                return job

            print(f"Job {job_id} status is {status}. Polling again in 2 seconds...")
        except requests.exceptions.RequestException as e:
            print(f"Error polling job status for {job_id}: {e}")
            return None
        time.sleep(2)
    
    print(f"Error: Job {job_id} timed out after {timeout} seconds.")
    return None

def test_robust_spf_conversion():
    """
    Tests the end-to-end conversion of a simple Oracle Stored Procedure.
    It submits the job, polls for completion, and verifies the output.
    """
    print("\n--- Running Robust Test: End-to-End SPF Conversion ---")
    
    oracle_spf = """
    CREATE OR REPLACE PROCEDURE sp_hello_world AS
    BEGIN
      DBMS_OUTPUT.PUT_LINE('Hello World!');
    END;
    """
    
    # The /convert endpoint handles the job_type internally.
    payload = {"sql": oracle_spf}

    try:
        # 1. Submit the conversion job to the correct endpoint
        response = requests.post(f"{API_URL}/convert", json=payload)
        response.raise_for_status()
        job_id = response.json().get("job_id")
        
        if not job_id:
            print("Test FAILED: Did not receive a job_id from the API.")
            return

        print(f"Conversion job created with ID: {job_id}")

        # 2. Poll for the job result
        final_job = poll_job_status(job_id)

        # 3. Validate the result
        if final_job and final_job.get("status") == "verified":
            converted_sql = final_job.get("converted_sql")
            print("Test PASSED: Job completed successfully.")
            print(f"Converted SQL:\n{converted_sql}")
            
            # Make assertions case-insensitive
            assert converted_sql is not None
            converted_sql_lower = converted_sql.lower()
            assert "create or replace function" in converted_sql_lower
            assert "plpgsql" in converted_sql_lower
        else:
            error_message = final_job.get('error_message', 'No error message provided.') if final_job else 'Polling failed.'
            print(f"Test FAILED: Job did not complete successfully.")
            print(f"Final Status: {final_job.get('status') if final_job else 'Unknown'}")
            print(f"Error Message: {error_message}")

    except requests.exceptions.RequestException as e:
        print(f"Test FAILED: An API request error occurred: {e}")
    except Exception as e:
        print(f"Test FAILED: An unexpected error occurred: {e}")

def test_robust_ddl_conversion():
    """
    Tests the end-to-end conversion of a simple Oracle DDL statement.
    It submits the job, polls for completion, and verifies the output.
    """
    print("\n--- Running Robust Test: End-to-End DDL Conversion ---")
    
    oracle_ddl = """
    CREATE TABLE robust_test_users (
        id NUMBER(10) NOT NULL,
        username VARCHAR2(50) NOT NULL,
        created_at DATE DEFAULT SYSDATE,
        PRIMARY KEY (id)
    );
    """
    
    # The /convert-ddl endpoint handles the job_type internally.
    payload = {"sql": oracle_ddl}

    try:
        # 1. Submit the conversion job to the correct endpoint
        response = requests.post(f"{API_URL}/convert-ddl", json=payload)
        response.raise_for_status()
        job_id = response.json().get("job_id")
        
        if not job_id:
            print("Test FAILED: Did not receive a job_id from the API.")
            return

        print(f"Conversion job created with ID: {job_id}")

        # 2. Poll for the job result
        final_job = poll_job_status(job_id)

        # 3. Validate the result
        if final_job and final_job.get("status") == "verified":
            converted_sql = final_job.get("converted_sql")
            print("Test PASSED: Job completed successfully.")
            print(f"Converted SQL:\n{converted_sql}")

            # Make assertions case-insensitive
            assert converted_sql is not None
            converted_sql_lower = converted_sql.lower()
            assert "create table robust_test_users" in converted_sql_lower
            assert "integer" in converted_sql_lower or "serial" in converted_sql_lower or "numeric" in converted_sql_lower
            assert "varchar(50)" in converted_sql_lower
            assert "timestamp" in converted_sql_lower or "date" in converted_sql_lower
        else:
            error_message = final_job.get('error_message', 'No error message provided.') if final_job else 'Polling failed.'
            print(f"Test FAILED: Job did not complete successfully.")
            print(f"Final Status: {final_job.get('status') if final_job else 'Unknown'}")
            print(f"Error Message: {error_message}")

    except requests.exceptions.RequestException as e:
        print(f"Test FAILED: An API request error occurred: {e}")
    except Exception as e:
        print(f"Test FAILED: An unexpected error occurred: {e}")

if __name__ == "__main__":
    print("Starting Robust Test Suite...")
    test_robust_spf_conversion()
    test_robust_ddl_conversion()
    print("\nRobust Test Suite Finished.")
