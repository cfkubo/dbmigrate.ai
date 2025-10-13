from fastapi import APIRouter, HTTPException
from .. import models
from .. import oracle_helper
from .. import database
import pika

router = APIRouter()

@router.post("/connect")
async def connect_to_oracle(details: models.OracleConnectionDetails):
    try:
        schemas = oracle_helper.get_oracle_schemas(details)
        return {"schemas": schemas}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-extraction")
async def test_extraction(details: models.OracleConnectionDetails):
    try:
        message = oracle_helper.test_oracle_ddl_extraction(details)
        return {"message": message}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list-objects")
async def list_objects(request: models.ListObjectsRequest):
    try:
        objects = oracle_helper.list_oracle_objects(request.connection_details, request.schema_name, request.object_type)
        return {"objects": objects}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract")
async def extract_ddl(request: models.ExtractRequest):
    parent_job_id = None
    try:
        parent_job_id = database.create_ddl_parent_job()
        ddls = oracle_helper.get_oracle_ddl(request.connection_details, request.schemas, request.object_types, request.object_names, request.select_all)

        for obj_type, objects in ddls.items():
            if obj_type == "db_name":
                continue

            table_name = f"{obj_type.lower()}_extraction_jobs"

            for obj_name, ddl in objects.items():
                database.create_ddl_child_job(parent_job_id, ddl, table_name)

        return {"parent_job_id": parent_job_id}
    except RuntimeError as e:
        if parent_job_id:
            database.update_job_status(parent_job_id, 'failed', 'ddl_jobs', error_message=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except pika.exceptions.AMQPError as e:
        if parent_job_id:
            database.update_job_status(parent_job_id, 'failed', 'ddl_jobs', error_message=f"Failed to publish message to RabbitMQ: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to publish message to RabbitMQ: {e}")
