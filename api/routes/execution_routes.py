from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
import psycopg2
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .. import models
from .. import execution_logic
from .. import queues
from .. import database # Added this import
from ..models import MigrationDetails

router = APIRouter()

@router.post("/test-postgres-connection")
async def test_postgres_connection(details: models.PostgresConnectionDetails):
    try:
        conn = psycopg2.connect(
            dbname=details.dbname,
            user=details.user,
            password=details.password,
            host=details.host,
            port=details.port
        )
        conn.close()
        return JSONResponse(content={"message": "Connection successful!"})
    except psycopg2.Error as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {e}")

@router.post("/create-database")
async def create_database(details: models.PostgresConnectionDetails):
    try:
        success = database.create_postgres_database(
            host=details.host,
            port=details.port,
            user=details.user,
            password=details.password,
            dbname_to_create=details.dbname
        )
        if success:
            return JSONResponse(content={"message": f"Database '{details.dbname}' created successfully or already exists."})
        else:
            raise HTTPException(status_code=500, detail=f"Failed to create database '{details.dbname}'. Check logs for details.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.post("/execute-sql")
async def execute_sql_file(file: UploadFile = File(...), pg_creds_json: str = Form(...), is_verification: bool = Form(False)):
    content = await file.read()
    connection = queues.get_rabbitmq_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Failed to connect to RabbitMQ.")
    try:
        pg_creds = json.loads(pg_creds_json)
        job_id = execution_logic.process_sql_file(content.decode(), file.filename, pg_creds, connection, is_verification=is_verification)
        logger.debug(f"Returning job_id {job_id} for /execute-sql")
        return JSONResponse(status_code=202, content={"job_id": job_id})
    except (json.JSONDecodeError, RuntimeError) as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection and connection.is_open:
            connection.close()

@router.post("/start-migration")
async def start_migration(migration_details: MigrationDetails):
    try:
        job_id = await execution_logic.initiate_migration_pipeline(migration_details)
        return JSONResponse(status_code=202, content={"job_id": job_id, "message": "Migration initiated successfully."})
    except Exception as e:
        logger.error(f"Error initiating migration: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initiate migration: {e}")
