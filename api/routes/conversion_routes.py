import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Response, Form
from fastapi.responses import JSONResponse
import json
import os
import re
import pika
import sqlparse
from opentelemetry import trace
from opentelemetry.propagate import inject

from .. import models
from .. import database
from .. import queues
from ..sanitizer import sanitize_for_execution # Import the new sanitizer

router = APIRouter()
logger = logging.getLogger(__name__) # Use a logger instance

@router.post("/convert")
async def convert_oracle_to_postgres(conversion_input: models.ConversionInput):
    """
    Submits one or more stored procedures/blocks for conversion.
    """
    job_type = conversion_input.job_type
    # Use the new sanitizer, which handles splitting based on job_type
    procedures = sanitize_for_execution(conversion_input.sql, job_type)
    job_ids = []

    if not procedures:
        raise HTTPException(status_code=400, detail="No valid SQL statements found to convert.")

    connection = queues.get_rabbitmq_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Failed to connect to RabbitMQ.")

    try:
        channel = connection.channel()
        for proc in procedures:
            job_id = database.create_job(proc, job_type)
            job_ids.append(job_id)
            carrier = {}
            inject(carrier)
            channel.basic_publish(
                exchange='',
                routing_key='conversion_jobs',
                body=json.dumps({'job_id': job_id, 'parent_job_id': job_id, 'original_sql': proc, 'job_type': job_type}),
                properties=pika.BasicProperties(delivery_mode=2, headers=carrier)
            )
        channel.close()
    except pika.exceptions.AMQPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish message to RabbitMQ: {e}")
    finally:
        if connection and connection.is_open:
            connection.close()

    json_content = json.dumps({"job_ids": job_ids}) + "\n"
    return Response(content=json_content, media_type="application/json", status_code=202)

# ---

@router.post("/convert-file")
async def convert_oracle_to_postgres_file(file: UploadFile = File(...)):
    job_type = "sql"
    content = await file.read()
    # Use the new sanitizer for file-based conversions as well
    procedures = sanitize_for_execution(content.decode(), job_type)
    job_ids = []

    connection = queues.get_rabbitmq_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Failed to connect to RabbitMQ.")

    try:
        channel = connection.channel()
        for proc in procedures:
            job_id = database.create_job(proc, job_type)
            job_ids.append(job_id)
            carrier = {}
            inject(carrier)
            channel.basic_publish(
                exchange='',
                routing_key='conversion_jobs',
                body=json.dumps({'job_id': job_id, 'parent_job_id': job_id, 'original_sql': proc, 'job_type': job_type}),
                properties=pika.BasicProperties(delivery_mode=2, headers=carrier)
            )
        channel.close()
    except pika.exceptions.AMQPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish message to RabbitMQ: {e}")
    finally:
        if connection and connection.is_open:
            connection.close()

    json_content = json.dumps({"job_ids": job_ids}) + "\n"
    return Response(content=json_content, media_type="application/json", status_code=202)

# ---





# ---

@router.post("/reconvert-with-suggestions")
async def reconvert_with_suggestions(reconversion_input: models.ReconversionInput):
    """
    Resubmits an existing job with potential modifications or suggestions for reconversion.
    """
    job_id = reconversion_input.job_id
    new_original_sql = reconversion_input.new_original_sql

    job = database.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found.")

    original_sql = new_original_sql if new_original_sql is not None else job['original_sql']
    job_type = job['job_type']

    suggestions = []
    if job.get('error_message'):
        try:
            suggestions = json.loads(job['error_message'])
            if not isinstance(suggestions, list):
                suggestions = [str(suggestions)]
        except json.JSONDecodeError:
            logger.warning(f"Job {job_id} error_message is not valid JSON for suggestions: {job['error_message']}")
            suggestions = [job['error_message']]
    
    connection = queues.get_rabbitmq_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Failed to connect to RabbitMQ.")

    try:
        channel = connection.channel()
        carrier = {}
        inject(carrier)

        channel.basic_publish(
            exchange='',
            routing_key='conversion_jobs',
            body=json.dumps({'job_id': job_id, 'parent_job_id': job_id, 'original_sql': original_sql, 'job_type': job_type, 'suggestions': suggestions}),
            properties=pika.BasicProperties(delivery_mode=2, headers=carrier)
        )
        channel.close()
    except pika.exceptions.AMQPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish message to RabbitMQ: {e}")
    finally:
        if connection and connection.is_open:
            connection.close()

    database.update_job_status(job_id, 'pending', converted_sql=None, error_message=None)

    json_content = json.dumps({"job_id": job_id, "status": "reconversion_initiated"}) + "\n"
    return Response(content=json_content, media_type="application/json", status_code=202)
