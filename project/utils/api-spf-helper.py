# gradio_app.py
import gradio as gr
import requests
import time
import datetime
import os
from typing import Optional

# Configuration
API_URL = "http://127.0.0.1:8000"

def submit_and_retrieve_sql(oracle_sql: str) -> str:
    """
    Submits an Oracle SQL DDL statement to the FastAPI backend,
    polls for job completion, saves the converted SQL to a file,
    and returns the result for display.
    """
    if not oracle_sql.strip():
        return "Please enter a SQL statement to convert."

    # 1. Submit the DDL to the FastAPI backend
    try:
        response = requests.post(f"{API_URL}/convert-ddl", json={"sql": oracle_sql.strip()})
        response.raise_for_status()
        job_id = response.json().get("job_id")
    except requests.exceptions.RequestException as e:
        return f"Error connecting to the API: {e}"

    # 2. Poll the job status until it is complete
    status = "pending"
    converted_sql = None
    error_message = None

    while status not in ["verified", "failed"]:
        try:
            time.sleep(1) # Wait for 1 second before polling again
            response = requests.get(f"{API_URL}/job/{job_id}")
            response.raise_for_status()
            job_details = response.json()
            status = job_details.get("status")
            if status == "verified":
                converted_sql = job_details.get("converted_sql")
            elif status == "failed":
                error_message = job_details.get("error_message")
        except requests.exceptions.RequestException as e:
            return f"Error retrieving job status: {e}"

    # 3. Handle the final result
    if status == "verified":
        # Write the converted SQL to a file with a timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"converted_sql_{timestamp}.sql"
        try:
            with open(filename, "w") as f:
                f.write(converted_sql)
            return f"Conversion successful! Converted SQL saved to '{os.path.abspath(filename)}'\n\n-- Converted SQL:\n{converted_sql}"
        except IOError as e:
            return f"Conversion successful, but failed to write to file: {e}\n\n-- Converted SQL:\n{converted_sql}"
    else:
        return f"Job failed. Reason: {error_message}"

# Create the Gradio interface
with gr.Blocks(title="Oracle to PostgreSQL DDL Converter") as demo:
    gr.Markdown(
        """
        # Oracle to PostgreSQL DDL Converter
        Submit your Oracle DDL statement below to convert it to PostgreSQL syntax.
        The converted SQL will be saved to a local file and displayed here.
        """
    )
    sql_input = gr.Textbox(
        label="Enter Oracle SQL DDL",
        lines=5,
        placeholder="e.g., CREATE TABLE users (id NUMBER, name VARCHAR2(100));"
    )
    submit_btn = gr.Button("Convert SQL")
    output_text = gr.Textbox(label="Result", lines=10, interactive=False)

    # Define the action for the button click
    submit_btn.click(
        fn=submit_and_retrieve_sql,
        inputs=sql_input,
        outputs=output_text
    )

if __name__ == "__main__":
    demo.launch()
