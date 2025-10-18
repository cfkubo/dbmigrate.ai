import logging
logging.basicConfig(level=logging.INFO)
logging.info("Starting app.py")

import gradio as gr
from dotenv import load_dotenv

load_dotenv()

import os
import pandas as pd
import git
import tempfile
import mermaid as md

# Import functions from the new gradio_callbacks.py

from ui.gradio_callbacks import dm_connect_and_get_oracle_schemas
from ui.gradio_callbacks import dm_connect_and_get_postgres_schemas
from ui.gradio_callbacks import dm_list_oracle_tables
from ui.gradio_callbacks import dm_list_postgres_tables
from ui.gradio_callbacks import dm_start_migration
from ui.gradio_callbacks import dm_check_status
from ui import api_client
from ui.gradio_callbacks import dm_get_oracle_table_ddl
from ui.gradio_callbacks import dm_get_postgres_table_ddl
from ui.gradio_callbacks import poll_job_status
from ui.gradio_callbacks import convert_sql_from_text
from ui.gradio_callbacks import poll_aggregate_status
from ui.gradio_callbacks import convert_from_file

from ui.gradio_callbacks import connect_to_oracle
from ui.gradio_callbacks import test_extraction
from ui.gradio_callbacks import list_objects_for_schema
from ui.gradio_callbacks import extract_ddl
from ui.gradio_callbacks import poll_ddl_job
from ui.gradio_callbacks import get_git_info
from ui.gradio_callbacks import toggle_connection_input
from ui.gradio_callbacks import show_list_objects_button
from ui.gradio_callbacks import select_all_objects
from ui.gradio_callbacks import test_pg_connection
from ui.gradio_callbacks import create_database_frontend
from ui.gradio_callbacks import submit_sql_file
from ui.gradio_callbacks import poll_sql_job_status
from ui.gradio_callbacks import get_job_types_from_api
from ui.gradio_callbacks import get_jobs_data
from ui.gradio_callbacks import update_jobs_view
from ui.gradio_callbacks import on_load
from ui.gradio_callbacks import on_search_change
from ui.gradio_callbacks import on_status_change
from ui.gradio_callbacks import on_job_type_change
from ui.gradio_callbacks import on_prev_click
from ui.gradio_callbacks import on_next_click
from ui.gradio_callbacks import get_code_metrics # Import the new function

from ui.gradio_callbacks import gini_full_workflow

logging.info("Imports complete")

def get_code_review_data():
    # Call the new get_code_metrics function from gradio_callbacks
    return get_code_metrics()

# API_URL is now imported from config.py, no longer defined here
# from config import API_URL # This import is not needed in app.py as API_URL is used only in gradio_callbacks.py

mermaid_code = """
graph TD
    A[Start] --> B[Step 1]
    B --> C[Step 2]
    C --> D[End]
"""

# with open("projectsExplain.md", "r") as f:
#     project_explanation = f.read()

with open("project/prj-docs/prjmd.md", "rb") as f:
    prjmd_doc = f.read()

with open("project/prj-docs/prj_inspiration.md", "rb") as f:
    prj_inspiration = f.read()

# def get_git_commit_hash():
#     raise NotImplementedError

with gr.Blocks() as demo:
    gr.Markdown("# DbMigrate.AI ")

    with gr.Tab("✨DbMigrate.AI"):
        with gr.Row(equal_height=True):
            gr.Image("assets/ora.png", scale=1, show_download_button=False, show_fullscreen_button=False, label="Oracle")
            gr.Image("assets/dbai.png", scale=5, show_download_button=False, show_fullscreen_button=False,  label="Migration Tool")
            gr.Image("assets/pg.png", scale=1, show_download_button=False, show_fullscreen_button=False, label="PostgreSQL")


    with gr.Tab("✨Extract Oracle DB MetatData"):
        with gr.Row():
            with gr.Column():
                host = gr.Textbox(label="Host", value=os.getenv("ORACLE_HOST", "localhost"))
                port = gr.Number(label="Port", value=os.getenv("ORACLE_PORT", 1521))
                user = gr.Textbox(label="Username", value=os.getenv("ORACLE_USER", "SYSTEM"))
                password = gr.Textbox(label="Password", type="password", value=os.getenv("ORACLE_PASSWORD", "password"))
                connection_type = gr.Radio(["Service Name", "SID"], label="Connection Type", value="Service Name")
                service_name_input = gr.Textbox(label="Service Name", value=os.getenv("ORACLE_SERVICE_NAME", "FREEPDB1"), visible=True)
                sid_input = gr.Textbox(label="SID", value=os.getenv("ORACLE_SID", "free"), visible=False)
                connect_button = gr.Button("Connect", variant="primary")

                schemas_checkbox = gr.CheckboxGroup(label="Select Schemas", visible=False)
                object_types_radio = gr.Radio(label="Select Object Type", choices=["TABLE", "PROCEDURE", "FUNCTION", "INDEX", "PACKAGE", "VIEW", "TRIGGER"], value="TABLE", visible=False)
                list_objects_button = gr.Button("List Objects", visible=False)
                objects_checkbox = gr.CheckboxGroup(label="Select Objects", visible=False)
                all_objects_state = gr.State()
                select_all_objects_checkbox = gr.Checkbox(label="Select All", visible=False)
                extract_button = gr.Button("Generate SQL", visible=False)
                test_extraction_button = gr.Button("Test Extraction", visible=False)
                ddl_download_file = gr.File(label="Download DDLs", visible=False)

            with gr.Column():
                output_text = gr.HTML(label="Output")
                child_jobs_df = gr.DataFrame(label="Child Job Statuses", visible=True)

        connection_type.change(toggle_connection_input, connection_type, [service_name_input, sid_input])

        object_types_radio.change(show_list_objects_button, object_types_radio, [list_objects_button, extract_button])

        connect_button.click(
            connect_to_oracle,
            inputs=[host, port, user, password, service_name_input, sid_input, connection_type],
            outputs=[output_text, schemas_checkbox, object_types_radio, list_objects_button, test_extraction_button, extract_button],
        )

        test_extraction_button.click(
            test_extraction,
            inputs=[host, port, user, password, service_name_input, sid_input, connection_type],
            outputs=output_text,
        )

        list_objects_button.click(
            list_objects_for_schema,
            inputs=[host, port, user, password, service_name_input, sid_input, connection_type, schemas_checkbox, object_types_radio],
            outputs=[objects_checkbox, select_all_objects_checkbox, all_objects_state],
        )

        extract_button.click(
            extract_ddl,
            inputs=[host, port, user, password, service_name_input, sid_input, connection_type, schemas_checkbox, object_types_radio, objects_checkbox, select_all_objects_checkbox],
            outputs=[output_text, child_jobs_df, ddl_download_file],
        )

        select_all_objects_checkbox.change(
            select_all_objects,
            inputs=[select_all_objects_checkbox, all_objects_state],
            outputs=[objects_checkbox]
        )

    with gr.Tab("✨Gini"):
        with gr.Row():
            with gr.Column():
                gini_host = gr.Textbox(label="Host", value=os.getenv("ORACLE_HOST", "localhost"))
                gini_port = gr.Number(label="Port", value=os.getenv("ORACLE_PORT", 1521))
                gini_user = gr.Textbox(label="Username", value=os.getenv("ORACLE_USER", "SYSTEM"))
                gini_password = gr.Textbox(label="Password", type="password", value=os.getenv("ORACLE_PASSWORD", "password"))
                gini_connection_type = gr.Radio(["Service Name", "SID"], label="Connection Type", value="Service Name")
                gini_service_name_input = gr.Textbox(label="Service Name", value=os.getenv("ORACLE_SERVICE_NAME", "FREEPDB1"), visible=True)
                gini_sid_input = gr.Textbox(label="SID", value=os.getenv("ORACLE_SID", "free"), visible=False)
                gini_connect_button = gr.Button("Connect to Oracle", variant="primary")

                gini_schemas_checkbox = gr.CheckboxGroup(label="Select Schemas", visible=False)
                gini_object_types_radio = gr.Radio(label="Select Object Type", choices=["TABLE", "PROCEDURE", "FUNCTION", "INDEX", "PACKAGE", "VIEW", "TRIGGER"], value="TABLE", visible=False)
                gini_list_objects_button = gr.Button("List Objects", visible=False)
                gini_objects_checkbox = gr.CheckboxGroup(label="Select Objects", visible=False)
                gini_all_objects_state = gr.State()
                gini_select_all_objects_checkbox = gr.Checkbox(label="Select All", visible=False)
                gini_start_gini_process_button = gr.Button("Start Gini Process", variant="primary", visible=False)

            with gr.Column():
                gini_output_text = gr.HTML(label="Output")
                gini_ddl_download_file = gr.File(label="Downloaded DDLs", visible=False)
                gini_converted_sql_output = gr.Textbox(label="Converted PostgreSQL SQL", interactive=False, lines=10, visible=False)
                gini_migration_status = gr.Textbox(label="Data Migration Status", interactive=False, visible=False)
                gini_migration_progress = gr.Number(label="Data Migration Progress", visible=False)

        gini_connection_type.change(toggle_connection_input, gini_connection_type, [gini_service_name_input, gini_sid_input])

        gini_object_types_radio.change(show_list_objects_button, gini_object_types_radio, [gini_list_objects_button, gini_start_gini_process_button])

        gini_connect_button.click(
            connect_to_oracle,
            inputs=[gini_host, gini_port, gini_user, gini_password, gini_service_name_input, gini_sid_input, gini_connection_type],
            outputs=[gini_output_text, gini_schemas_checkbox, gini_object_types_radio, gini_list_objects_button, gini_start_gini_process_button],
        )

        gini_list_objects_button.click(
            list_objects_for_schema,
            inputs=[gini_host, gini_port, gini_user, gini_password, gini_service_name_input, gini_sid_input, gini_connection_type, gini_schemas_checkbox, gini_object_types_radio],
            outputs=[gini_objects_checkbox, gini_select_all_objects_checkbox, gini_all_objects_state],
        )

        gini_select_all_objects_checkbox.change(
            select_all_objects,
            inputs=[gini_select_all_objects_checkbox, gini_all_objects_state],
            outputs=[gini_objects_checkbox]
        )

        # The gini_start_gini_process_button.click will be wired up in the next step
        with gr.Accordion("PostgreSQL Connection Details", open=False):
            gini_pg_host = gr.Textbox(label="PostgreSQL Host", value=os.getenv("POSTGRES_HOST", "localhost"))
            gini_pg_port = gr.Number(label="PostgreSQL Port", value=os.getenv("POSTGRES_PORT", 5432))
            gini_pg_user = gr.Textbox(label="PostgreSQL User", value=os.getenv("POSTGRES_USER", "postgres"))
            gini_pg_password = gr.Textbox(label="PostgreSQL Password", type="password", value=os.getenv("POSTGRES_PASSWORD", "postgres"))

        gini_start_gini_process_button.click(
            gini_full_workflow,
            inputs=[
                gini_host, gini_port, gini_user, gini_password, gini_service_name_input, gini_sid_input, gini_connection_type,
                gini_schemas_checkbox, gini_object_types_radio, gini_objects_checkbox, gini_select_all_objects_checkbox,
                gini_pg_host, gini_pg_port, gini_pg_user, gini_pg_password
            ],
            outputs=[
                gini_output_text, gini_converted_sql_output, gini_migration_status, gini_migration_progress
            ]
        )

    with gr.Tab("✨(AI) SQL Conversion"):
        with gr.Row():
            text_input = gr.Textbox(lines=20, label="Oracle SQL")
            text_output = gr.Textbox(lines=20, label="Converted PostgreSQL", interactive=False)
        text_status = gr.Textbox(label="Status", interactive=False)
        text_button = gr.Button("Convert", variant="primary")
        download_button_text = gr.DownloadButton(label="Download SQL", visible=False)

        text_button.click(
            convert_sql_from_text, # Changed from convert_from_text
            inputs=[text_input],
            outputs=[text_status, text_output, download_button_text]
        )

    with gr.Tab("✨(AI) SQL File Conversion"):
        file_input = gr.File(label="Upload Oracle Stored Procedure File")
        with gr.Accordion("PostgreSQL Connection Details for Conversion", open=False):
            spf_bulk_pg_host = gr.Textbox(label="Host", value=os.getenv("POSTGRES_HOST", "localhost"))
            spf_bulk_pg_port = gr.Number(label="Port", value=os.getenv("POSTGRES_PORT", 5432))
            spf_bulk_pg_user = gr.Textbox(label="User", value=os.getenv("POSTGRES_USER", "postgres"))
            spf_bulk_pg_pass = gr.Textbox(label="Password", type="password", value=os.getenv("POSTGRES_PASSWORD", "postgres"))
            spf_bulk_pg_db = gr.Textbox(label="Database", value=os.getenv("POSTGRES_DB", "postgres"))
        with gr.Row():
            successful_output = gr.Textbox(lines=20, label="Successful Conversions", interactive=False)
            failed_output = gr.Textbox(lines=20, label="Failed Conversions", interactive=False)
        file_status = gr.Textbox(label="Status", interactive=False, lines=5)
        file_button = gr.Button("Convert", variant="primary")
        with gr.Row():
            download_button_successful = gr.DownloadButton(label="Download Successful SQL", visible=False)
            download_button_failed = gr.DownloadButton(label="Download Failed SQL", visible=False)

        file_button.click(
            convert_from_file,
            inputs=[
                file_input,
                spf_bulk_pg_host,
                spf_bulk_pg_port,
                spf_bulk_pg_user,
                spf_bulk_pg_pass,
                spf_bulk_pg_db,
                gr.Textbox(value="sql", visible=False)
            ],
            outputs=[file_status, successful_output, failed_output, download_button_successful, download_button_failed]
        )



    with gr.Tab("✨PSQL Executor"):
        gr.Markdown("## Execute SQL Script on PostgreSQL")
        gr.Markdown("Upload a .sql file to execute its content against the specified PostgreSQL database. The execution is tracked as a job.")
        sql_exec_job_id_state = gr.State(value=None)
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### PostgreSQL Connection")
                sql_exec_pg_host = gr.Textbox(label="Host", value=os.getenv("POSTGRES_HOST", "localhost"))
                sql_exec_pg_port = gr.Number(label="Port", value=os.getenv("POSTGRES_PORT", 5432))
                sql_exec_pg_user = gr.Textbox(label="User", value=os.getenv("POSTGRES_USER", "postgres"))
                sql_exec_pg_pass = gr.Textbox(label="Password", type="password", value=os.getenv("POSTGRES_PASSWORD", "postgres"))
                sql_exec_pg_db = gr.Textbox(label="Database", value=os.getenv("POSTGRES_DB", "postgres"))
                sql_exec_pg_port.visible = True
                sql_exec_pg_user.visible = True
                sql_exec_pg_pass.visible = True
                sql_exec_pg_db.visible = True

                sql_exec_create_db_if_not_exists = gr.Checkbox(label="Create Database if not exists", value=False)
                sql_exec_create_db_button = gr.Button("Create Database", variant="stop")
                sql_exec_test_button = gr.Button("Test Connection", variant="stop")
                sql_exec_conn_status = gr.Textbox(label="Connection Status", interactive=False)

            with gr.Column(scale=2):
                gr.Markdown("### SQL File Upload")
                sql_exec_file_input = gr.File(label="Upload .sql File")
                sql_exec_button = gr.Button("Execute SQL", variant="primary")
                sql_exec_status = gr.Textbox(label="Job Status", interactive=False)
                sql_exec_details = gr.JSON(label="Job Details", visible=False)
                sql_exec_statement_results = gr.DataFrame(label="Statement Execution Results", visible=False, headers=["Statement", "Status", "Error"])

        sql_exec_button.click(
            submit_sql_file,
            inputs=[
                sql_exec_file_input,
                sql_exec_pg_host,
                sql_exec_pg_port,
                sql_exec_pg_user,
                sql_exec_pg_pass,
                sql_exec_pg_db
            ],
            outputs=[sql_exec_status, sql_exec_job_id_state, sql_exec_details, sql_exec_statement_results]
        )

        sql_exec_create_db_button.click(
            create_database_frontend,
            inputs=[
                sql_exec_pg_host,
                sql_exec_pg_port,
                sql_exec_pg_user,
                sql_exec_pg_pass,
                sql_exec_pg_db
            ],
            outputs=sql_exec_conn_status # Display status in the same connection status box
        )

        sql_exec_test_button.click(
            test_pg_connection,
            inputs=[
                sql_exec_pg_host,
                sql_exec_pg_port,
                sql_exec_pg_user,
                sql_exec_pg_pass
            ],
            outputs=sql_exec_conn_status
        )

    with gr.Tab("✨Data Migration"):
        print("Initializing Data Migration Tab")
        gr.Markdown("## Oracle to PostgreSQL Data Migration")
        dm_task_id_state = gr.Textbox(visible=False, label="Task ID")
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Oracle Connection")
                dm_ora_host = gr.Textbox(label="Host", value=os.getenv("ORACLE_HOST", "localhost"))
                dm_ora_port = gr.Number(label="Port", value=os.getenv("ORACLE_PORT", 1521))
                dm_ora_user = gr.Textbox(label="User", value=os.getenv("ORACLE_USER", "SYSTEM"))
                dm_ora_pass = gr.Textbox(label="Password", type="password", value=os.getenv("ORACLE_PASSWORD", "password"))
                dm_ora_service = gr.Textbox(label="Service Name", value=os.getenv("ORACLE_SERVICE_NAME", "freepdb1"))
                dm_ora_connect_btn = gr.Button("Connect to Oracle", variant="primary" )
                dm_ora_status = gr.Textbox(label="Connection Status", interactive=False, visible=False)
                dm_ora_schema = gr.Dropdown(label="Oracle Source Schema", interactive=False, visible=False)
                dm_ora_list_tables_btn = gr.Button("List Oracle Tables", visible=False)
                dm_ora_tables = gr.Dropdown(label="Oracle Source Table", interactive=False, visible=False) # Moved definition
            dm_ora_connect_btn.click(
                dm_connect_and_get_oracle_schemas,
                inputs=[dm_ora_user, dm_ora_pass, dm_ora_host, dm_ora_port, dm_ora_service],
                outputs=[dm_ora_schema, dm_ora_status, dm_ora_list_tables_btn]
            )
            dm_ora_list_tables_btn.click(
                dm_list_oracle_tables,
                inputs=[dm_ora_user, dm_ora_pass, dm_ora_host, dm_ora_port, dm_ora_service, dm_ora_schema],
                outputs=[dm_ora_tables, dm_ora_status]
            )
            with gr.Column(scale=1):
                gr.Markdown("### PostgreSQL Connection")
                dm_pg_host = gr.Textbox(label="Host", value=os.getenv("POSTGRES_HOST", "localhost"))
                dm_pg_port = gr.Number(label="Port", value=os.getenv("POSTGRES_PORT", 5432))
                dm_pg_user = gr.Textbox(label="User", value=os.getenv("POSTGRES_USER", "postgres"))
                dm_pg_pass = gr.Textbox(label="Password", type="password", value=os.getenv("POSTGRES_PASSWORD", "postgres"))
                dm_pg_db = gr.Textbox(label="Database", value=os.getenv("POSTGRES_DB", "postgres"))
                dm_pg_connect_btn = gr.Button("Connect to PostgreSQL", variant="primary")
                dm_pg_status = gr.Textbox(label="Connection Status", interactive=False, visible=False)
                dm_pg_schema = gr.Dropdown(label="PostgreSQL Destination Schema", interactive=False, visible=False)
                dm_pg_list_tables_btn = gr.Button("List PostgreSQL Tables", visible=False)
                dm_pg_tables = gr.Dropdown(label="PostgreSQL Destination Table", interactive=False, visible=False) # Moved definition
            dm_pg_connect_btn.click(
                dm_connect_and_get_postgres_schemas,
                inputs=[dm_pg_user, dm_pg_pass, dm_pg_host, dm_pg_port, dm_pg_db],
                outputs=[dm_pg_schema, dm_pg_status, dm_pg_list_tables_btn]
            )
            dm_pg_list_tables_btn.click(
                dm_list_postgres_tables,
                inputs=[dm_pg_user, dm_pg_pass, dm_pg_host, dm_pg_port, dm_pg_db, dm_pg_schema],
                outputs=[dm_pg_tables, dm_pg_status]
            )
        with gr.Row():
            with gr.Column(scale=1):
                dm_ora_ddl = gr.Textbox(label="Oracle Table DDL", interactive=False, visible=False, lines=10)
            with gr.Column(scale=1):
                dm_pg_ddl = gr.Textbox(label="PostgreSQL Table DDL", interactive=False, visible=False, lines=10)

        dm_ora_tables.change(
            dm_get_oracle_table_ddl,
            inputs=[dm_ora_user, dm_ora_pass, dm_ora_host, dm_ora_port, dm_ora_service, dm_ora_schema, dm_ora_tables],
            outputs=[dm_ora_ddl]
        )

        dm_pg_tables.change(
            dm_get_postgres_table_ddl,
            inputs=[dm_pg_user, dm_pg_pass, dm_pg_host, dm_pg_port, dm_pg_db, dm_pg_schema, dm_pg_tables],
            outputs=[dm_pg_ddl]
        )
        with gr.Row():
            with gr.Column():
                pass # Removed redundant dm_ora_tables definition
            with gr.Column():
                pass # Removed redundant dm_pg_tables definition
        dm_overall_status = gr.Textbox(label="Migration Status", interactive=False)
        dm_progress = gr.Number(label="Migration Progress")
        dm_schema_error_display = gr.Markdown(label="Schema Comparison Errors", visible=False)
        with gr.Row():
            dm_migrate_btn = gr.Button("Migrate Data", variant="primary")
            dm_refresh_btn = gr.Button("Refresh Status")
            dm_migrate_btn.click(
                dm_start_migration,
                inputs=[
                    dm_ora_user,
                    dm_ora_pass,
                    dm_ora_host,
                        dm_ora_port,
                        dm_ora_service,
                        dm_ora_schema,
                        dm_pg_user,
                        dm_pg_pass,
                        dm_pg_host,
                        dm_pg_port,
                        dm_pg_db,
                        dm_pg_schema,
                        dm_ora_tables,
                        dm_pg_tables
                    ],
                    outputs=[dm_overall_status, dm_task_id_state, dm_schema_error_display]
                )

            dm_refresh_btn.click(
                dm_check_status,
                inputs=[dm_task_id_state],
                outputs=[dm_overall_status, dm_progress],
            )

    # with gr.Tab("Project Architecture"):
    #     gr.Markdown(project_explanation)


    # display jobs information in a nice table format using gradio components i have expose the data in main.py with this code



    with gr.Tab("⚙️All Jobs⚙️"):
        # import pandas as pd # Already imported at the top
        # from datetime import datetime # Already imported at the top

        with gr.Row():
            job_type_dropdown = gr.Dropdown(label="Select Job Type", choices=[], value=None)
            search_bar = gr.Textbox(label="Search by Job ID or SQL content")
            status_dropdown = gr.Dropdown(choices=["all", "pending", "verified", "failed"], value="all", label="Filter by Status")

        jobs_df = gr.DataFrame(label="Jobs", wrap=True)
        status_text = gr.Textbox(label="Status", interactive=False)

        with gr.Row():
            prev_button = gr.Button("Previous", variant="primary")
            page_num_input = gr.Number(label="Page", value=1, precision=0)
            next_button = gr.Button("Next", variant="primary")

        total_pages_state = gr.Number(value=1, visible=False, label="Total Pages")

        job_type_dropdown.change(on_job_type_change, [job_type_dropdown, search_bar, status_dropdown], [jobs_df, status_text, total_pages_state, page_num_input])
        demo.load(on_load, [], [job_type_dropdown, jobs_df, status_text, total_pages_state, page_num_input])
        search_bar.submit(on_search_change, [job_type_dropdown, search_bar, status_dropdown], [jobs_df, status_text, total_pages_state, page_num_input])
        status_dropdown.change(on_status_change, [job_type_dropdown, search_bar, status_dropdown], [jobs_df, status_text, total_pages_state, page_num_input])
        prev_button.click(on_prev_click, [job_type_dropdown, page_num_input, search_bar, status_dropdown, total_pages_state], [jobs_df, status_text, total_pages_state, page_num_input])
        next_button.click(on_next_click, [job_type_dropdown, page_num_input, search_bar, status_dropdown, total_pages_state], [jobs_df, status_text, total_pages_state, page_num_input])


    with gr.Tab("Code Review"):
        gr.Markdown("## Code Review")
        gr.Markdown("This tab shows the number of lines of code for key Python files in the project.")
        code_review_df = gr.DataFrame(label="Code Review", wrap=True)
        refresh_button = gr.Button("Refresh")

        def refresh_code_review():
            return get_code_review_data()

        refresh_button.click(
            refresh_code_review,
            outputs=[code_review_df]
        )
        demo.load(refresh_code_review, outputs=[code_review_df])

    with gr.Tab("✨Project Plan & Explanation"):
        gr.Image("assets/dbai.png", scale=1, show_download_button=False, show_fullscreen_button=False, label="Architecture Diagram")
        gr.Markdown(prjmd_doc.decode("utf-8"))
        gr.Image("assets/logo1.png", scale=1, show_download_button=False, show_fullscreen_button=False, label="Architecture Diagram")


    with gr.Tab("✨Project Inspiration"):
        gr.Image("assets/dbai.png", scale=1, show_download_button=False, show_fullscreen_button=False, label="Architecture Diagram")

        gr.Markdown(prj_inspiration.decode("utf-8"))

        gr.Image("assets/logo1.png", scale=1, show_download_button=False, show_fullscreen_button=False, label="Architecture Diagram")



    # Create the Gradio interface to display Git information
    with gr.Row():
        gr.Markdown("##### Git Information Display")

    # Use a Textbox to display the information
    git_output = gr.Textbox(
        label="Current Git Status",
        value=get_git_info(),
        interactive=False, # Don't allow users to edit this
        lines=2,
        max_lines=2
    )


logging.info("Launching Gradio UI")
demo.launch(mcp_server=True) 