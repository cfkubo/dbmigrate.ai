import gradio as gr
import requests
import time
from datetime import datetime
import os
import json
import pandas as pd
import git
import tempfile
from ui import api_client
from config import API_URL # Import API_URL from the new config file









def dm_connect_and_get_oracle_schemas(user, password, host, port, service_name):
    try:
        oracle_credentials = {
            "user": user,
            "password": password,
            "host": host,
            "port": port,
            "service_name": service_name
        }
        schemas = api_client.get_oracle_schemas(oracle_credentials)
        if not schemas:
            return gr.update(choices=[], value=None, interactive=True, visible=True), gr.update(value="Connected to Oracle, but no schemas found or accessible. Check permissions or connection details.", visible=True), gr.update(visible=False)
        return gr.update(choices=schemas, value=None, interactive=True, visible=True), gr.update(value=f"Connected to Oracle. Found {len(schemas)} schemas.", visible=True), gr.update(visible=True)
    except Exception as e:
        return gr.update(choices=[], value=None, interactive=True, visible=False), gr.update(value=str(e), visible=True), gr.update(visible=False)

def dm_connect_and_get_postgres_schemas(user, password, host, port, dbname):
    try:
        postgres_credentials = {
            "user": user,
            "password": password,
            "host": host,
            "port": port,
            "dbname": dbname
        }
        schemas = api_client.get_postgres_schemas(postgres_credentials)
        return gr.update(choices=schemas, value=None, interactive=True, visible=True), gr.update(value=f"Connected to PostgreSQL. Found {len(schemas)} schemas.", visible=True), gr.update(visible=True)
    except Exception as e:
        return gr.update(choices=[], value=None, interactive=True, visible=False), gr.update(value=str(e), visible=True), gr.update(visible=False)

def dm_list_oracle_tables(user, password, host, port, service_name, schema_name):
    try:
        oracle_credentials = {
            "user": user,
            "password": password,
            "host": host,
            "port": port,
            "service_name": service_name
        }
        tables = api_client.get_oracle_tables(oracle_credentials, schema_name)
        return gr.update(choices=tables, value=None, interactive=True, visible=True), gr.update(value=f"Found {len(tables)} tables in schema {schema_name}.", visible=True)
    except Exception as e:
        return gr.update(choices=[], value=None, interactive=True, visible=False), gr.update(value=str(e), visible=True)

def dm_list_postgres_tables(user, password, host, port, dbname, schema_name):
    try:
        postgres_credentials = {
            "user": user,
            "password": password,
            "host": host,
            "port": port,
            "dbname": dbname
        }
        tables = api_client.get_postgres_tables(postgres_credentials, schema_name)
        return gr.update(choices=tables, value=None, interactive=True, visible=True), gr.update(value=f"Found {len(tables)} tables in schema {schema_name}.", visible=True)
    except Exception as e:
        return gr.update(choices=[], value=None, interactive=True, visible=False), gr.update(value=str(e), visible=True)

def dm_start_migration(ora_user, ora_pass, ora_host, ora_port, ora_service, ora_schema, pg_user, pg_pass, pg_host, pg_port, pg_db, pg_schema, ora_table, pg_table):
    ora_creds = {'user': ora_user, 'password': ora_pass, 'host': ora_host, 'port': ora_port, 'service_name': ora_service}
    pg_creds = {'user': pg_user, 'password': pg_pass, 'host': pg_host, 'port': pg_port, 'dbname': pg_db}
    if not all(ora_creds.values()) or not all(pg_creds.values()) or not ora_schema or not ora_table or not pg_schema or not pg_table:
        return "Error: All fields are required.", None, gr.update(visible=False, value="")

    result = api_client.start_migration(ora_creds, pg_creds, ora_schema, ora_table, pg_schema, pg_table)

    if result["status"] == "success":
        return f"Migration task {result['job_id']} submitted.", result['job_id'], gr.update(visible=False, value="")
    else:
        error_detail = result["detail"]
        formatted_error = "### Schema Comparison Failed! ###\n\n"
        if "message" in error_detail:
            formatted_error += f"**Message:** {error_detail['message']}\n\n"
        if "issues" in error_detail and error_detail["issues"]:
            formatted_error += "**Issues Found:**\n"
            for issue in error_detail["issues"]:
                formatted_error += f"- {issue}\n"
            formatted_error += "\n"
        if "oracle_ddl" in error_detail:
            formatted_error += "**Oracle DDL:**\n```sql\n"
            formatted_error += error_detail["oracle_ddl"]
            formatted_error += "\n```\n\n"
        if "postgres_ddl" in error_detail:
            formatted_error += "**PostgreSQL DDL:**\n```sql\n"
            formatted_error += error_detail["postgres_ddl"]
            formatted_error += "\n```"
        return "Migration failed due to schema incompatibility. See details below.", None, gr.update(visible=True, value=formatted_error)

def dm_check_status(task_id):
    if not task_id:
        return "", 0.0
    try:
        status_data = api_client.check_migration_status(task_id)
        status = status_data.get('status', 'unknown')
        message = status_data.get('message', '')
        progress = status_data.get('progress', None)

        if progress:
            return f"Status: {status} - {message}", float(progress.strip('%'))/100
        else:
            return f"Status: {status} - {message}", 0.0
    except Exception as e:
        return f"Error checking status: {e}", 0.0

def dm_get_oracle_table_ddl(user, password, host, port, service_name, schema_name, table_name):
    if not table_name:
        return gr.update(visible=False, value="")
    try:
        oracle_credentials = {
            "user": user,
            "password": password,
            "host": host,
            "port": port,
            "service_name": service_name
        }
        ddl = api_client.get_oracle_table_ddl(oracle_credentials, schema_name, table_name)
        return gr.update(visible=True, value=ddl)
    except Exception as e:
        return gr.update(visible=True, value=f"Error fetching DDL: {e}")

def dm_get_postgres_table_ddl(user, password, host, port, dbname, schema_name, table_name):
    if not table_name:
        return gr.update(visible=False, value="")
    try:
        postgres_credentials = {
            "user": user,
            "password": password,
            "host": host,
            "port": port,
            "dbname": dbname
        }
        ddl = api_client.get_postgres_table_ddl(postgres_credentials, schema_name, table_name)
        return gr.update(visible=True, value=ddl)
    except Exception as e:
        return gr.update(visible=True, value=f"Error fetching DDL: {e}")

def get_jobs_data_old(): # Renamed to avoid conflict with the one in All Jobs tab
    try:
        response = requests.get(f"{API_URL}/jobs")
        response.raise_for_status()
        jobs = response.json()
        if not jobs:
            return pd.DataFrame(), "No jobs found."
        # Convert to pandas DataFrame for easier display in Gradio
        df = pd.DataFrame(jobs)
        # Reorder columns for better readability
        cols = ['job_id', 'status', 'job_type', 'error_message', 'original_sql', 'converted_sql']
        # Ensure all columns are present, fill missing with empty string
        for col in cols:
            if col not in df.columns:
                df[col] = ""
        df = df[cols]
        return df, "Jobs loaded successfully."
    except requests.exceptions.RequestException as e:
        return pd.DataFrame(), f"Error fetching jobs: {e}"

def poll_job_status(job_id):
    """Polls the job status endpoint until the job is complete."""
    while True:
        try:
            response = requests.get(f"{API_URL}/jobs/job/{job_id}")
            response.raise_for_status()
            job = response.json()
            print(f"Polling job {job_id}, received: {job}")
            status = job.get("status")
            yield f"Job ID: {job_id} - Status: {status}", "", gr.update(visible=False)

            # --- FIX: Handle all failure statuses and simplify output ---
            if status in ["completed", "verified", "failed", "failed", "ai_failed"]:
                converted_sql = job.get("converted_sql", "")
                error_message = job.get("error_message", "")

                if status in ["failed", "failed", "ai_failed"]:
                    # Combine the error and the last attempted SQL for clarity
                    final_output = f"-- Conversion Status: {status}\n"
                    final_output += f"-- Error: {error_message}\n\n"
                    final_output += f"-- Last Attempted SQL:\n{converted_sql}"
                else:
                    final_output = converted_sql

                now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"converted-file-{now}.sql"

                # Use a temporary directory for file storage
                temp_dir = tempfile.gettempdir()
                filepath = os.path.join(temp_dir, filename)

                with open(filepath, "w") as f:
                    f.write(final_output)

                yield f"Job {status}", final_output, gr.update(value=filepath, visible=True)
                break
            # --- END FIX ---

        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            try:
                error_detail = e.response.json().get("detail", error_detail)
            except (ValueError, AttributeError):
                pass
            yield f"Error: {error_detail}", "", gr.update(visible=False)
            break
        time.sleep(1)


def convert_sql_from_text(text):
    """Sends text to the SPF conversion API and polls for the result."""
    print(f"Sending text for SPF conversion: {text[:100]}...")
    try:
        response = requests.post(f"{API_URL}/convert", json={"sql": text, "job_type": "sql"})
        response.raise_for_status()
        data = response.json()
        job_ids = data.get("job_ids")
        if not job_ids:
            yield "Error: No job IDs received from the API.", "", gr.update(visible=False)
            return
        job_id = job_ids[0]
        yield from poll_job_status(job_id)
    except requests.exceptions.RequestException as e:
        error_detail = str(e)
        try:
            error_detail = e.response.json().get("detail", error_detail)
        except (ValueError, AttributeError):
            pass
        yield f"Error: {error_detail}", "", gr.update(visible=False)


def poll_aggregate_status(job_ids):
    """Polls the aggregate jobs endpoint until all jobs are complete."""
    while True:
        try:
            response = requests.post(f"{API_URL}/jobs/aggregate", json={"job_ids": job_ids})
            response.raise_for_status()
            result = response.json()
            print(f"Polling aggregate status for jobs {job_ids}, received: {result}")
            status = result.get("status")

            if status == "processing":
                pending_count = result.get("pending_jobs", 0)
                total_count = result.get("total_jobs", len(job_ids))
                yield f"Job IDs: {', '.join(job_ids)} - Processing... {total_count - pending_count}/{total_count} jobs complete.", "", "", gr.update(visible=False), gr.update(visible=False)
            elif status == "completed":
                successful_sql = result.get("successful_sql", "")
                failed_jobs = result.get("failed_jobs", [])

                failed_sql_formatted = []
                if failed_jobs:
                    for job in failed_jobs:
                        original_sql = job.get("original_sql", "No original SQL provided.")
                        error_message = job.get("error_message", "No error message provided.")
                        failed_sql_formatted.append(f"---\n-- Failure Reason: {error_message}\n---\n{original_sql}\n")

                failed_sql_output = "\n".join(failed_sql_formatted)

                now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                successful_filename = f"successful-{now}.sql"
                failed_filename = f"failed-{now}.sql"

                if successful_sql:
                    with open(successful_filename, "w") as f:
                        f.write(successful_sql)

                if failed_sql_output:
                    with open(failed_filename, "w") as f:
                        f.write(failed_sql_output)

                yield f"Job IDs: {', '.join(job_ids)} - Completed", successful_sql, failed_sql_output, gr.update(value=successful_filename, visible=True if successful_sql else False), gr.update(value=failed_filename, visible=True if failed_sql_output else False)
                break

        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            try:
                error_detail = e.response.json().get("detail", error_detail)
            except (ValueError, AttributeError):
                pass
            yield f"Error: {error_detail}", "", "", gr.update(visible=False), gr.update(visible=False)
            break
        time.sleep(2)

def convert_from_file(file, pg_host, pg_port, pg_user, pg_pass, pg_db, job_type='sql'):
    pg_creds = {
        "host": pg_host,
        "port": int(pg_port),
        "user": pg_user,
        "password": pg_pass,
        "dbname": pg_db
    }
    print(f"Sending file for conversion: {file.name}")
    """Sends a file to the conversion API and polls for the aggregate result."""
    try:
        with open(file.name, 'rb') as f:
            original_filename = getattr(file, 'orig_name', os.path.basename(file.name))
            files = {'file': (original_filename, f, 'application/sql')}
            # Assuming pg_creds is available in this scope or passed correctly
            # If not, it needs to be passed as a separate form field or JSON payload
            data = {'pg_creds_json': json.dumps(pg_creds), 'job_type': job_type}
            response = requests.post(f"{API_URL}/convert-file", files=files, data=data)
            response.raise_for_status()
            job_ids = response.json().get("job_ids")
            if job_ids:
                yield from poll_aggregate_status(job_ids)
            else:
                yield "No jobs created.", "", "", gr.update(visible=False), gr.update(visible=False)
    except requests.exceptions.RequestException as e:
        error_detail = str(e)
        try:
            error_detail = e.response.json().get("detail", error_detail)
        except (ValueError, AttributeError):
            pass
        yield f"Error: {error_detail}", "", "", gr.update(visible=False), gr.update(visible=False)

def connect_to_oracle(host, port, user, password, service_name, sid, connection_type):
    """
    Calls the backend API to connect to the Oracle database and get a list of schemas.
    """
    payload = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
    }
    if connection_type == "Service Name":
        payload["service_name"] = service_name
    else:
        payload["sid"] = sid

    try:
        response = requests.post(f"{API_URL}/api/oracle/connect", json=payload)
        response.raise_for_status()
        data = response.json()
        schemas = data.get("schemas", [])
        return "Connected successfully. Please select schemas and object types to extract.", gr.update(choices=schemas, visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)
    except requests.exceptions.RequestException as e:
        error_detail = str(e)
        try:
            error_detail = e.response.json().get("detail", error_detail)
        except (ValueError, AttributeError):
            pass
        return f"Error: {error_detail}", gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

def test_extraction(host, port, user, password, service_name, sid, connection_type):
    """
    Calls the backend API to test DDL extraction.
    """
    connection_details = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
    }
    if connection_type == "Service Name":
        connection_details["service_name"] = service_name
    else:
        connection_details["sid"] = sid

    try:
        response = requests.post(f"{API_URL}/test-extraction", json=connection_details)
        response.raise_for_status()
        data = response.json()
        return data["message"]
    except requests.exceptions.RequestException as e:
        error_detail = str(e)
        try:
            error_detail = e.response.json().get("detail", error_detail)
        except (ValueError, AttributeError):
            pass
        return f"Error: {error_detail}"

def list_objects_for_schema(host, port, user, password, service_name, sid, connection_type, schemas, object_type):
    """
    Calls the backend API to list objects for a given schema and object type.
    """
    if not schemas:
        return gr.update(choices=[], visible=True), gr.update(visible=False), []
    schema = schemas[0] # Use the first selected schema

    connection_details = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
    }
    if connection_type == "Service Name":
        connection_details["service_name"] = service_name
    else:
        connection_details["sid"] = sid

    payload = {
        "connection_details": connection_details,
        "schema_name": schema,
        "object_type": object_type,
    }
    try:
        response = requests.post(f"{API_URL}/api/oracle/list-objects", json=payload)
        response.raise_for_status()
        data = response.json()
        objects = data.get("objects", [])
        return gr.update(choices=objects, visible=True), gr.update(visible=True), objects
    except requests.exceptions.RequestException as e:
        error_detail = str(e)
        try:
            error_detail = e.response.json().get("detail", error_detail)
        except (ValueError, AttributeError):
            pass
        return gr.update(choices=[], visible=True), gr.update(visible=False), []

def extract_ddl(host, port, user, password, service_name, sid, connection_type, schemas, object_types, object_names, select_all=False):
    """
    Calls the backend API to extract DDLs for the selected schemas and object types.
    """
    connection_details = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
    }
    if connection_type == "Service Name":
        connection_details["service_name"] = service_name
    else:
        connection_details["sid"] = sid

    payload = {
        "connection_details": connection_details,
        "schemas": schemas,
        "object_types": [object_types],
        "object_names": object_names,
        "select_all": select_all,
    }
    try:
        response = requests.post(f"{API_URL}/api/oracle/extract", json=payload)
        response.raise_for_status()
        data = response.json()
        parent_job_id = data.get("parent_job_id")

        if not parent_job_id:
            return "Failed to create a job.", None

        yield from poll_ddl_job(parent_job_id)

    except requests.exceptions.RequestException as e:
        error_detail = str(e)
        try:
            error_detail = e.response.json().get("detail", error_detail)
        except (ValueError, AttributeError):
            pass
        return f"Error: {error_detail}", None

def poll_ddl_job(job_id):
    """Polls the job result endpoint until the job is complete."""
    while True:
        try:
            # First, check the overall status
            response = requests.get(f"{API_URL}/jobs/job/{job_id}/result")

            if response.status_code == 200 and response.headers.get('Content-Type') == 'application/sql':
                now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"converted-ddl-{now}.sql"
                filepath = os.path.join(tempfile.gettempdir(), filename)
                with open(filepath, "wb") as f:
                    f.write(response.content)
                yield "Completed", pd.DataFrame(), gr.update(value=filepath, visible=True)
                break

            job = response.json()
            status = job.get("status")

            # Then, get detailed child job statuses
            child_jobs_response = requests.get(f"{API_URL}/jobs/job/{job_id}/children")
            child_jobs_data = child_jobs_response.json().get('child_jobs', [])
            child_jobs_df = pd.DataFrame(child_jobs_data)

            if status == "processing":
                pending = job.get("pending_jobs", 0)
                total = job.get("total_jobs", 0)
                yield f"<h3>Processing... {total - pending} / {total} DDLs extracted.</h3>", child_jobs_df, None
            elif status == "failed":
                yield f"Job failed: {job.get('failed_jobs')}", child_jobs_df, None
                break

        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            try:
                error_detail = e.response.json().get("detail", error_detail)
            except (ValueError, AttributeError):
                pass
            yield f"Error: {error_detail}", pd.DataFrame(), None
            break
        time.sleep(2)

def get_git_info():
        """
        Retrieves the current Git branch and commit hash.
        Returns:
            A formatted string with the branch and commit info, or an error message.
        """
        try:
            repo = git.Repo(search_parent_directories=True)
            branch = repo.active_branch.name
            commit = repo.head.commit.hexsha[:7]  # Get the short commit hash
            git_info = f"Branch: {branch}, Commit: {commit} ,     Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')},     Author: 'Arul Khanna Vannala + AI'"
            print(git_info)
            return git_info
        except git.InvalidGitRepositoryError:
            return "Not a Git repository."
        except Exception as e:
            return f"Error getting Git info: {e}"

def toggle_connection_input(connection_type):
    if connection_type == "Service Name":
        return gr.update(visible=True), gr.update(visible=False)
    else:
        return gr.update(visible=False), gr.update(visible=True)

def show_list_objects_button(object_type):
    return gr.update(visible=True), gr.update(visible=True)

def select_all_objects(select_all, all_objects_from_state):
    if select_all:
        return gr.update(value=all_objects_from_state)
    else:
        return gr.update(value=[])

def test_pg_connection(pg_host, pg_port, pg_user, pg_pass):
    # Test connection to the PostgreSQL server itself, not a specific database
    # by connecting to the 'postgres' database
    pg_creds = {
        "host": pg_host,
        "port": int(pg_port),
        "user": pg_user,
        "password": pg_pass,
        "dbname": "postgres" # Connect to default database
    }
    try:
        response = requests.post(f"{API_URL}/api/test-postgres-connection", json=pg_creds)
        response.raise_for_status()
        return response.json().get("message", "Connection to PostgreSQL server successful!")
    except requests.exceptions.RequestException as e:
        error_detail = str(e)
        try:
            error_detail = e.response.json().get("detail", error_detail)
        except (ValueError, AttributeError):
            pass
        return f"Error connecting to PostgreSQL server: {error_detail}"

def create_database_frontend(pg_host, pg_port, pg_user, pg_pass, pg_db):
    pg_creds = {
        "host": pg_host,
        "port": int(pg_port),
        "user": pg_user,
        "password": pg_pass,
        "dbname": pg_db
    }
    try:
        response = requests.post(f"{API_URL}/api/create-database", json=pg_creds)
        response.raise_for_status()
        return response.json().get("message", f"Database '{pg_db}' created successfully or already exists.")
    except requests.exceptions.RequestException as e:
        error_detail = str(e)
        try:
            error_detail = e.response.json().get("detail", error_detail)
        except (ValueError, AttributeError):
            pass
        return f"Error creating database: {error_detail}"

def submit_sql_file(file, pg_host, pg_port, pg_user, pg_pass, pg_db):
    if file is None:
        return "Please upload a file.", None, gr.update(visible=False), gr.update(visible=False)

    try:
        pg_creds = {
            "host": pg_host,
            "port": int(pg_port),
            "user": pg_user,
            "password": pg_pass,
            "dbname": pg_db
        }

        with open(file.name, 'rb') as f:
            original_filename = getattr(file, 'orig_name', os.path.basename(file.name))
            files = {'file': (original_filename, f, 'application/sql')}
            data = {'pg_creds_json': json.dumps(pg_creds)}
            response = requests.post(f"{API_URL}/api/execute-sql", files=files, data=data)
            response.raise_for_status()
            job_id = response.json().get("job_id")
            yield f"Job {job_id} submitted. Polling for status...", job_id, gr.update(visible=False), gr.update(visible=False)
            yield from poll_sql_job_status(job_id)

    except requests.exceptions.RequestException as e:
        error_detail = str(e)
        try:
            error_detail = e.response.json().get("detail", error_detail)
        except (ValueError, AttributeError):
            pass
        yield f"Error: {error_detail}", None, gr.update(visible=True, value={"error": error_detail}), gr.update(visible=False)
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        error_message = f"An unexpected error occurred: {str(e)}\n\nTraceback:\n{tb_str}"
        yield error_message, None, gr.update(visible=True, value={"error": error_message}), gr.update(visible=False)

def poll_sql_job_status(job_id):
    if not job_id:
        return
    time.sleep(2) # Add a small delay before starting to poll
    while True:
        try:
            response = requests.get(f"{API_URL}/jobs/sql-execution-job/{job_id}")
            response.raise_for_status()
            job = response.json()
            status = job.get("status")
            statement_results = job.get("statement_results", [])

            df_results = pd.DataFrame(statement_results) if statement_results else pd.DataFrame(columns=["statement", "status", "error"])

            yield f"Job Status: {status}", job_id, gr.update(visible=True, value=job), gr.update(value=df_results, visible=bool(statement_results))

            if status in ["completed", "failed"]:
                break
        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            try:
                error_detail = e.response.json().get("detail", error_detail)
            except (ValueError, AttributeError):
                pass
            yield f"Error polling job status: {error_detail}", job_id, gr.update(visible=True, value={"error": error_detail}), gr.update(visible=False)
            break
        time.sleep(2)

def get_job_types_from_api():
    try:
        response = requests.get(f"{API_URL}/jobs/types")
        response.raise_for_status()
        job_types = response.json()
        print(f"Fetched job types: {job_types}")
        return job_types
    except requests.exceptions.RequestException as e:
        print(f"Error fetching job types: {e}")
        return []

def gini_full_workflow(
    ora_host, ora_port, ora_user, ora_password, ora_service_name, ora_sid, ora_connection_type,
    ora_schemas, ora_object_types, ora_object_names, ora_select_all,
    pg_host, pg_port, pg_user, pg_password
):
    # Initialize outputs
    yield "Starting Gini workflow...", "", "", 0.0

    oracle_credentials = {
        "host": ora_host,
        "port": ora_port,
        "user": ora_user,
        "password": ora_password,
    }
    if ora_connection_type == "Service Name":
        oracle_credentials["service_name"] = ora_service_name
        pg_db_name = ora_service_name.lower().replace('-', '_') # Use service name for PG DB
    else:
        oracle_credentials["sid"] = ora_sid
        pg_db_name = ora_sid.lower().replace('-', '_') # Use SID for PG DB

    pg_credentials = {
        "host": pg_host,
        "port": pg_port,
        "user": pg_user,
        "password": pg_password,
        "dbname": pg_db_name # This will be the new DB name
    }

    extracted_ddl_content = ""
    converted_sql_content = ""

    try:
        # Step 1: Extract Oracle DDLs
        yield "Step 1/5: Extracting Oracle DDLs...", converted_sql_content, "", 0.1

        # Call the extract_ddl function to get the parent_job_id
        # The extract_ddl function already handles the API call and polling
        # We need to capture the yielded values from poll_ddl_job
        ddl_extraction_generator = extract_ddl(
            ora_host, ora_port, ora_user, ora_password, ora_service_name, ora_sid, ora_connection_type,
            ora_schemas, ora_object_types, ora_object_names, ora_select_all
        )

        for status_msg, child_df, ddl_file_path_obj in ddl_extraction_generator:
            yield f"Step 1/5: {status_msg}", converted_sql_content, "", 0.1 + (0.1 * 0.5) # Update progress
            if ddl_file_path_obj and isinstance(ddl_file_path_obj, dict) and "value" in ddl_file_path_obj:
                ddl_file_path = ddl_file_path_obj["value"]
                with open(ddl_file_path, 'r') as f:
                    extracted_ddl_content = f.read()
                os.remove(ddl_file_path) # Clean up the temporary DDL file
                break # DDL extraction complete

        if not extracted_ddl_content:
            raise Exception("Failed to extract Oracle DDLs.")

        yield "Step 1/5: Oracle DDL extraction completed.", converted_sql_content, "", 0.2

        # Step 2: AI Convert DDLs
        yield "Step 2/5: Converting DDLs to PostgreSQL...", converted_sql_content, "", 0.3

        # Call convert_ddl_from_text and poll for its status
        conversion_generator = convert_sql_from_text(extracted_ddl_content)
        for status_msg, converted_sql, download_path in conversion_generator:
            yield f"Step 2/5: {status_msg}", converted_sql, "", 0.3 + (0.1 * 0.5) # Update progress
            if "Job completed" in status_msg or "Job failed" in status_msg: # Check for completion or failure
                converted_sql_content = converted_sql
                break

        if not converted_sql_content:
            raise Exception("Failed to convert DDLs to PostgreSQL.")

        yield "Step 2/5: DDL conversion completed.", converted_sql_content, "", 0.4

        # Step 3: Create New PostgreSQL Database
        yield f"Step 3/5: Creating PostgreSQL database '{pg_db_name}'...", converted_sql_content, "", 0.5

        # Use the create_database_frontend callback
        create_db_message = create_database_frontend(pg_host, pg_port, pg_user, pg_password, pg_db_name)
        if "Error" in create_db_message:
            raise Exception(f"Failed to create PostgreSQL database: {create_db_message}")

        yield f"Step 3/5: {create_db_message}", converted_sql_content, "", 0.6

        # Step 4: Execute Converted SQLs on New PostgreSQL Database
        yield "Step 4/5: Executing converted SQLs on PostgreSQL...", converted_sql_content, "", 0.7

        # Write converted_sql_content to a temporary file for submit_sql_file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".sql") as temp_sql_file:
            temp_sql_file.write(converted_sql_content)
            temp_sql_file_path = temp_sql_file.name

        # Create a mock file object that submit_sql_file can use
        file_obj = lambda: None
        file_obj.name = temp_sql_file_path
        file_obj.orig_name = "converted.sql"

        sql_execution_generator = submit_sql_file(
            file_obj, # Pass the mock file object
            pg_host, pg_port, pg_user, pg_password, pg_db_name
        )

        sql_execution_status = ""
        for status_msg, job_id, details, statement_results in sql_execution_generator:
            yield f"Step 4/5: {status_msg}", converted_sql_content, "", 0.7 + (0.1 * 0.5) # Update progress
            sql_execution_status = status_msg
            if "completed" in status_msg.lower() or "failed" in status_msg.lower():
                break

        os.remove(temp_sql_file_path) # Clean up temp file

        if "failed" in sql_execution_status.lower():
            raise Exception(f"Failed to execute converted SQLs: {sql_execution_status}")

        yield "Step 4/5: Converted SQLs executed successfully.", converted_sql_content, "", 0.8

        # Step 5: Initiate Data Migration
        yield "Step 5/5: Initiating data migration...", converted_sql_content, "", 0.9

        # For simplicity, let's assume we migrate all tables from the selected Oracle schema
        # This part needs more detailed logic to get actual table names
        # For now, I'll use a placeholder or assume a single table for demonstration
        # In a real scenario, you'd list tables from Oracle and iterate
        if not ora_object_names:
            raise Exception("No Oracle objects selected for data migration.")

        migration_job_ids = []
        for table_name in ora_object_names:
            # Assuming destination schema and table name are the same as source for simplicity
            migration_result = dm_start_migration(
                ora_user, ora_password, ora_host, ora_port, ora_service_name, ora_schemas[0], # Assuming single schema selection
                pg_user, pg_password, pg_host, pg_port, pg_db_name, ora_schemas[0], # Assuming single schema selection
                table_name, table_name
            )
            if migration_result["status"] == "success":
                migration_job_ids.append(migration_result["job_id"])
            else:
                raise Exception(f"Failed to start migration for table {table_name}: {migration_result['detail']}")

        yield f"Step 5/5: Data migration jobs submitted: {migration_job_ids}. Polling status...", converted_sql_content, "Data migration initiated.", 0.95

        # Poll for overall migration status (this part might need a new aggregate polling function)
        # For now, just report submission
        yield "Gini workflow completed successfully!", converted_sql_content, "Data migration initiated.", 1.0

    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        error_message = f"Gini Workflow Error: {str(e)}\n\nTraceback:\n{tb_str}"
        yield error_message, converted_sql_content, "", 0.0 # Reset progress on error
    try:
        response = requests.get(f"{API_URL}/jobs/types")
        response.raise_for_status()
        job_types = response.json()
        print(f"Fetched job types: {job_types}")
        return job_types
    except requests.exceptions.RequestException as e:
        print(f"Error fetching job types: {e}")
        return []

def get_jobs_data(table_name, page_num, page_size, search_term, status_filter):
    if not table_name:
        return pd.DataFrame(), "Please select a job type.", 1
    try:
        params = {
            "page": page_num,
            "size": page_size,
            "search": search_term,
            "status": status_filter,
        }
        response = requests.get(f"{API_URL}/jobs/{table_name}", params=params)
        response.raise_for_status()
        data = response.json()
        jobs = data.get("jobs", [])
        print(f"DEBUG: Jobs data received for {table_name}: {jobs[:2]}") # Print first 2 jobs for brevity
        total_pages = data.get("total_pages", 1)

        if not jobs:
            return pd.DataFrame(), "No jobs found.", 1

        df = pd.DataFrame(jobs)
        cols = ['job_id', 'status', 'job_type', 'created_at', 'error_message', 'original_sql', 'converted_sql']
        for col in cols:
            if col not in df.columns:
                df[col] = ""

        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')

        # Process error_message for AI feedback
        df['converted_sql_with_feedback'] = df['converted_sql']
        for index, row in df.iterrows():
            if row['status'] in ['ai_failed', 'ai_review_needed', 'ai_retrying'] and row['error_message']:
                try:
                    issues = json.loads(row['error_message'])
                    if isinstance(issues, list):
                        feedback_str = "\nAI Suggestions/Issues:\n- " + "\n- ".join(issues)
                    else:
                        feedback_str = "\nAI Feedback: " + str(issues)
                    df.loc[index, 'converted_sql_with_feedback'] = str(row['converted_sql']) + feedback_str
                except json.JSONDecodeError:
                    df.loc[index, 'converted_sql_with_feedback'] = str(row['converted_sql']) + "\nError parsing AI feedback: " + row['error_message']
            elif row['status'] == 'failed':
                df.loc[index, 'converted_sql_with_feedback'] = str(row['converted_sql']) + "\nError: " + str(row['error_message'])

        # Update the columns to display
        cols = ['job_id', 'status', 'job_type', 'created_at', 'error_message', 'original_sql', 'converted_sql_with_feedback']
        return df[cols], f"Page {page_num} of {total_pages}", total_pages
    except requests.exceptions.RequestException as e:
        error_detail = str(e)
        try:
            error_detail = e.response.json().get("detail", error_detail)
        except (ValueError, AttributeError):
            pass
        return pd.DataFrame(), f"Error fetching jobs: {error_detail}", 1
    except Exception as e:
        return pd.DataFrame(), f"An unexpected error occurred: {e}", 1

def update_jobs_view(table_name, page_num, search_term, status_filter):
    df, status, total_pages = get_jobs_data(table_name, page_num, 20, search_term, status_filter)
    return df, status, total_pages, page_num

def on_load():
    job_types = get_job_types_from_api()
    # If job_types is empty, set value to None to prevent Gradio error
    initial_value = job_types[0] if job_types else None
    df, status, total_pages, current_page_num = update_jobs_view(initial_value, 1, "", "all")
    return gr.update(choices=job_types, value=initial_value), df, status, total_pages, current_page_num

def on_search_change(table_name, search_term, status_filter):
    return update_jobs_view(table_name, 1, search_term, status_filter)

def on_status_change(table_name, search_term, status_filter):
    return update_jobs_view(table_name, 1, search_term, status_filter)

def on_job_type_change(table_name, search_term, status_filter):
    return update_jobs_view(table_name, 1, search_term, status_filter)

def on_prev_click(table_name, page_num, search_term, status_filter, total_pages):
    if page_num > 1:
        page_num -= 1
    return update_jobs_view(table_name, page_num, search_term, status_filter)

def on_next_click(table_name, page_num, search_term, status_filter, total_pages):
    if page_num < total_pages:
        page_num += 1
    return update_jobs_view(table_name, page_num, search_term, status_filter)