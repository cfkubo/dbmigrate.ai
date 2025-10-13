import requests
from config import API_URL

def start_migration(oracle_credentials, postgres_credentials, source_schema, source_table, destination_schema, destination_table):
    payload = {
        "oracle_credentials": oracle_credentials,
        "postgres_credentials": postgres_credentials,
        "source_schema": source_schema,
        "source_table": source_table,
        "destination_schema": destination_schema,
        "destination_table": destination_table,
    }
    try:
        response = requests.post(f"{API_URL}/migrate/start", json=payload)
        response.raise_for_status()
        return {"status": "success", "job_id": response.json()["job_id"]}
    except requests.exceptions.HTTPError as e:
        return {"status": "error", "detail": e.response.json()}

def check_migration_status(task_id):
    response = requests.get(f"{API_URL}/migrate/status/{task_id}")
    response.raise_for_status()
    return response.json()

def get_oracle_schemas(oracle_credentials):
    response = requests.post(f"{API_URL}/oracle/schemas", json=oracle_credentials)
    response.raise_for_status()
    return response.json()["schemas"]

def get_oracle_tables(oracle_credentials, schema_name):
    response = requests.post(f"{API_URL}/oracle/schemas/{schema_name}/tables", json=oracle_credentials)
    response.raise_for_status()
    return response.json()["tables"]

def get_postgres_schemas(postgres_credentials):
    response = requests.post(f"{API_URL}/postgres/schemas", json=postgres_credentials)
    response.raise_for_status()
    return response.json()["schemas"]

def get_postgres_tables(postgres_credentials, schema_name):
    response = requests.post(f"{API_URL}/postgres/schemas/{schema_name}/tables", json=postgres_credentials)
    response.raise_for_status()
    return response.json()["tables"]

def get_oracle_table_ddl(oracle_credentials, schema_name, table_name):
    response = requests.post(f"{API_URL}/oracle/schemas/{schema_name}/tables/{table_name}/ddl", json=oracle_credentials)
    response.raise_for_status()
    return response.json()["ddl"]

def get_postgres_table_ddl(postgres_credentials, schema_name, table_name):
    response = requests.post(f"{API_URL}/postgres/schemas/{schema_name}/tables/{table_name}/ddl", json=postgres_credentials)
    response.raise_for_status()
    return response.json()["ddl"]

def upload_document(filename: str, user_id: str, file_content: bytes):
    headers = {'X-User-ID': user_id}
    # The 'files' parameter in requests.post expects a tuple: (filename, file_content, content_type)
    files = {'files': (filename, file_content, 'application/pdf')}
    response = requests.post(f"{API_URL}/documents/upload", headers=headers, files=files)
    response.raise_for_status()
    return response.json()

def list_documents(user_id: str):
    headers = {'X-User-ID': user_id}
    response = requests.get(f"{API_URL}/documents", headers=headers)
    response.raise_for_status()
    return response.json().get("documents", [])