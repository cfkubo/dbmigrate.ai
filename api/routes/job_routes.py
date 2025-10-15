import logging
from fastapi import APIRouter, HTTPException, Response, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
from datetime import datetime
import os
import tempfile

from .. import models
from .. import database

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)

logger = logging.getLogger(__name__)



@router.get("/types")
def get_job_types():
    return database.get_job_table_names()



@router.get("/job/{job_id}")
def get_job_status(job_id: str):
    # --- Add validation for job_id ---
    if not job_id or job_id.lower() == "none":
        raise HTTPException(status_code=400, detail="Invalid job ID provided.")
    # --- End of validation ---

    job = database.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return database._convert_uuids_to_strings(dict(job))

@router.post("/aggregate")
def aggregate_job_results(aggregate_input: models.AggregateJobsInput, format: str = Query("json", enum=["json", "sql"])):
    logging.info(f"Received job_ids for aggregation: {aggregate_input.job_ids}")
    jobs = database.get_jobs_by_ids(aggregate_input.job_ids)
    logging.info(f"Jobs found by database.get_jobs_by_ids: {jobs}")
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found for the given IDs")

    pending_jobs = [str(job['job_id']) for job in jobs if job['status'] == 'pending']
    if pending_jobs:
        return JSONResponse(status_code=202, content={"status": "processing", "pending_jobs": len(pending_jobs), "total_jobs": len(aggregate_input.job_ids)})

    successful_sql = []
    failed_jobs = []
    for row in jobs:
        job = database._convert_uuids_to_strings(dict(row))
        status = job.get('status')
        if status in ('success', 'verified', 'completed'):
            successful_sql.append(job.get('converted_sql') or "")
        elif status in ('failed', 'failed'):
            failed_jobs.append({
                "original_sql": job.get('original_sql'),
                "error_message": job.get('error_message')
            })

    if format == "sql":
        all_sql = []
        if successful_sql:
            all_sql.append("-- Successful Conversions --")
            all_sql.extend(successful_sql)
        if failed_jobs:
            all_sql.append("-- Failed Conversions --")
            for failed_job in failed_jobs:
                error_comment = f"-- Job failed with error: {failed_job['error_message']}\n"
                all_sql.append(error_comment + (failed_job['original_sql'] or ""))
        return Response(content="\n/\n".join(all_sql), media_type="application/sql")
    else:
        return JSONResponse(content={"status": "completed", "successful_sql": "\n/\n".join(successful_sql), "failed_jobs": failed_jobs})

@router.get("/{table_name}")
def get_jobs_by_table(
    table_name: str,
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None,
) -> dict:
    allowed_tables = database.get_job_table_names()
    if table_name not in allowed_tables:
        raise HTTPException(status_code=404, detail="Job table not found")

    return database.get_paginated_jobs_from_table(table_name, page, size, search, status)

@router.get("/job/{job_id}/result")
def get_job_result(job_id: str):
    logger.debug(f"Received request for DDL job result for job_id: {job_id}")
    # --- Add validation for job_id ---
    if not job_id or job_id.lower() == "none":
        raise HTTPException(status_code=400, detail="Invalid job ID provided.")
    # --- End of validation ---

    child_jobs = database.get_all_child_job_statuses(job_id)
    
    if not child_jobs:
        raise HTTPException(status_code=404, detail="Job not found or no child jobs created.")

    pending_jobs = [job for job in child_jobs if job['status'] == 'pending']
    if pending_jobs:
        return {"status": "processing", "pending_jobs": len(pending_jobs), "total_jobs": len(child_jobs)}

    successful_sql = []
    failed_jobs = []
    for job in child_jobs:
        if job['status'] in ('success', 'verified'):
            successful_sql.append(job.get('converted_sql') or "")
        elif job['status'] == 'failed':
            failed_jobs.append(job)

    if not successful_sql:
        return {"status": "failed", "failed_jobs": failed_jobs}

    aggregated_sql = "\n/\n".join(successful_sql)
    
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"converted-ddl-{now}.sql"
    filepath = os.path.join(tempfile.gettempdir(), filename)
    with open(filepath, "w") as f:
        f.write(aggregated_sql)

    return FileResponse(filepath, media_type="application/sql", filename=filename)

@router.get("/job/{parent_job_id}/children")
def get_child_job_statuses(parent_job_id: str):
    logger.debug(f"Received request for DDL child job statuses for parent_job_id: {parent_job_id}")
    # --- Add validation for parent_job_id ---
    if not parent_job_id or parent_job_id.lower() == "none":
        raise HTTPException(status_code=400, detail="Invalid parent job ID provided.")
    # --- End of validation ---

    child_jobs = database.get_all_child_job_statuses(parent_job_id)
    if not child_jobs:
        raise HTTPException(status_code=404, detail="No child jobs found for the given parent ID.")
    
    return {"child_jobs": [database._convert_uuids_to_strings(dict(job)) for job in child_jobs]}

@router.get("/sql-execution-job/{job_id}")
def get_sql_execution_job_status(job_id: str):
    print(f"[DEBUG] get_sql_execution_job_status called for job_id: {job_id}")
    logger.debug(f"Received request for SQL execution job status for job_id: {job_id}")
    # --- Add validation for job_id ---
    if not job_id or job_id.lower() == "none":
        raise HTTPException(status_code=400, detail="Invalid job ID provided.")
    # --- End of validation ---

    job = database.get_sql_execution_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_dict = database._convert_uuids_to_strings(dict(job))
    submitted_at = job_dict.get("submitted_at")
    if isinstance(submitted_at, datetime):
        job_dict["submitted_at"] = submitted_at.isoformat()
    
    processed_at = job_dict.get("processed_at")
    if isinstance(processed_at, datetime):
        job_dict["processed_at"] = processed_at.isoformat()

    return JSONResponse(content=job_dict)
