import requests
import time
import os
import json

# It's a good practice to have the API_URL configurable or in a central place
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
SQL_ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'sql-assets')

def poll_job_status(job_id: str, timeout: int = 180): # Increased timeout to 180 seconds
    """
    Polls the job status endpoint until the job is complete or timeout is reached.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{API_URL}/jobs/job/{job_id}")
            response.raise_for_status()
            job = response.json()
            status = job.get("status")
            # SPF jobs use 'verified' or 'success' as successful states
            if status in ["verified", "success"]:
                return job
            elif status in ["failed", "failed"]: # Also return if failed to report status
                return job
        except requests.exceptions.RequestException as e:
            print(f"Error polling job status for {job_id}: {e}")
            time.sleep(2) # Wait before retrying
        time.sleep(2) # Wait before next poll
    print(f"Error: Job {job_id} timed out after {timeout} seconds.")
    return None

def test_bulk_spf_conversion():
    """
    Tests bulk SPF conversion using the oracle-sp-new.sql file.
    """
    print("\n--- Running Test: Bulk SPF Conversion ---")
    sql_file = os.path.join(SQL_ASSETS_DIR, 'oracle-sp-new.sql')
    
    if not os.path.exists(sql_file):
        print(f"Test SKIPPED: {sql_file} not found.")
        return

    with open(sql_file, 'r') as f:
        sql_content = f.read()

    payload = {"sql": sql_content, "job_type": "spf"}
    start_time = time.time()

    try:
        response = requests.post(f"{API_URL}/convert", json=payload)
        response.raise_for_status()
        job_ids = response.json().get("job_ids")
        
        if not job_ids:
            print("Test FAILED: Did not receive job_ids from the API.")
            return

        print(f"Submitted {len(job_ids)} SPF conversion jobs from {os.path.basename(sql_file)}.")
        success_count = 0
        
        for i, job_id in enumerate(job_ids):
            final_job = poll_job_status(job_id)
            if final_job and final_job.get("status") in ["verified", "success"]:
                success_count += 1
            else:
                status = final_job.get('status') if final_job else 'Unknown'
                print(f"  Job {i+1}/{len(job_ids)} (ID: {job_id}) FAILED with status: {status}")

        end_time = time.time()
        print(f"Finished SPF bulk test in {end_time - start_time:.2f} seconds.")
        print(f"  {success_count}/{len(job_ids)} jobs completed successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Test FAILED: An API request error occurred: {e}")
    except Exception as e:
        print(f"Test FAILED: An unexpected error occurred: {e}")

def test_bulk_ddl_conversion():
    """
    Tests bulk DDL conversion using the airline_schema.sql file.
    """
    print("\n--- Running Test: Bulk DDL Conversion ---")
    sql_file = os.path.join(SQL_ASSETS_DIR, 'airline_schema.sql')

    if not os.path.exists(sql_file):
        print(f"Test SKIPPED: {sql_file} not found.")
        return

    with open(sql_file, 'r') as f:
        sql_content = f.read()

    payload = {"sql": sql_content, "job_type": "ddl"}
    start_time = time.time()

    try:
        response = requests.post(f"{API_URL}/convert", json=payload)
        response.raise_for_status()
        job_ids = response.json().get("job_ids")

        if not job_ids:
            print("Test FAILED: Did not receive job_ids from the API.")
            return

        print(f"Submitted {len(job_ids)} DDL conversion jobs from {os.path.basename(sql_file)}.")
        success_count = 0

        for i, job_id in enumerate(job_ids):
            final_job = poll_job_status(job_id)
            # DDL jobs use 'verified' as a successful state. 'success' might also be possible.
            # 'failed' and 'failed' are failure states.
            if final_job and final_job.get("status") in ["verified", "success"]:
                success_count += 1
            else:
                status = final_job.get('status') if final_job else 'Unknown'
                print(f"  Job {i+1}/{len(job_ids)} (ID: {job_id}) FAILED with status: {status}")

        end_time = time.time()
        print(f"Finished DDL bulk test in {end_time - start_time:.2f} seconds.")
        print(f"  {success_count}/{len(job_ids)} jobs completed successfully.") # Corrected typo: len(job_ids)

    except requests.exceptions.RequestException as e:
        print(f"Test FAILED: An API request error occurred: {e}")
    except Exception as e:
        print(f"Test FAILED: An unexpected error occurred: {e}")

if __name__ == "__main__":
    print("Starting Bulk SQL Conversion Test Suite...")
    test_bulk_spf_conversion()
    test_bulk_ddl_conversion()
    print("\nBulk SQL Conversion Test Suite Finished.")
