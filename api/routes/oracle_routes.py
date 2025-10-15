from fastapi import APIRouter, HTTPException
from .. import models
from .. import oracle_helper
from .. import database
import pika
import json

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

from .. import queues

@router.post("/extract")
async def extract_ddl(request: models.ExtractRequest):
    parent_job_id = None
    try:
        parent_job_id = database.create_job(job_type='ddl_parent')
        ddls = oracle_helper.get_oracle_ddl(request.connection_details, request.schemas, request.object_types, request.object_names, request.select_all)

        for obj_type, objects in ddls.items():
            if obj_type == "db_name":
                continue

            queue_name = queues.QUEUE_CONFIG[obj_type]['queue']

            for obj_name, ddl in objects.items():
                job_id = database.create_job(
                    job_type='ddl_child', 
                    parent_job_id=parent_job_id, 
                    original_sql=ddl, 
                    object_type=obj_type, 
                    object_name=obj_name,
                    source_connection_details=request.connection_details.dict(),
                    source_schema=request.schemas[0] if request.schemas else None,
                    # These are placeholders, as they are not available in the request
                    target_schema=None, 
                    data_migration_enabled=False,
                    target_connection_details=None 
                )
                message = {
                    'job_id': job_id,
                    'parent_job_id': parent_job_id,
                    'source_connection': request.connection_details.dict(),
                    'object_type': obj_type,
                    'object_name': obj_name,
                    'source_schema': request.schemas[0] if request.schemas else None,
                    'target_schema': None, # Placeholder
                    'data_migration_enabled': False, # Placeholder
                    'target_connection': None # Placeholder
                }
                queues.publish_message(queue_name, json.dumps(message))

        return {"parent_job_id": parent_job_id}
    except RuntimeError as e:
        if parent_job_id:
            database.update_job_status(parent_job_id, 'failed', 'ddl_jobs', error_message=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except pika.exceptions.AMQPError as e:
        if parent_job_id:
            database.update_job_status(parent_job_id, 'failed', 'ddl_jobs', error_message=f"Failed to publish message to RabbitMQ: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to publish message to RabbitMQ: {e}")
