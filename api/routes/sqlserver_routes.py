
from fastapi import APIRouter, HTTPException
from .. import models
from .. import sqlserver_helper
from .. import queues
import pika
import json
from .. import database

router = APIRouter()

@router.post("/connect")
async def connect_to_sqlserver(details: models.SQLServerConnectionDetails):
    try:
        schemas = sqlserver_helper.get_sqlserver_schemas(details)
        return {"schemas": schemas}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list-objects")
async def list_objects(request: models.ListObjectsRequest): # Assuming a generic model for now
    try:
        objects = sqlserver_helper.list_sqlserver_objects(request.connection_details, request.schema_name, request.object_type)
        return {"objects": objects}
    except (RuntimeError, ValueError) as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract")
async def extract_ddl(request: models.ExtractRequest): # Assuming a generic model for now
    parent_job_id = None
    try:
        parent_job_id = database.create_job(job_type='ddl_parent')
        ddls = sqlserver_helper.get_sqlserver_ddl(request.connection_details, request.schemas, request.object_types, request.object_names, request.select_all)

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
                    target_schema=None, 
                    data_migration_enabled=False,
                    target_connection_details=None 
                )
                message = {
                    'job_id': job_id,
                    'parent_job_id': parent_job_id,
                    'source_db_type': 'sqlserver',
                    'source_connection': request.connection_details.dict(),
                    'object_type': obj_type,
                    'object_name': obj_name,
                    'source_schema': request.schemas[0] if request.schemas else None,
                    'target_schema': None, 
                    'data_migration_enabled': False, 
                    'target_connection': None 
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
