import logging
from fastapi import FastAPI, Response, Request, Form
import json
from opentelemetry.trace import get_current_span
from fastapi.middleware.cors import CORSMiddleware

from .routes import (conversion_routes, job_routes, oracle_routes,
                     execution_routes, migration_routes)
from .startup import lifespan
from .tracing import setup_tracing


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = FastAPI(lifespan=lifespan)

setup_tracing(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup_event():
    pass

@app.middleware("http")
async def add_trace_id_to_logs(request: Request, call_next):
    span = get_current_span()
    trace_id = span.context.trace_id
    # Convert the trace_id to a hexadecimal string for logging
    trace_id_hex = f"{trace_id:032x}" if trace_id != 0 else "no-trace-id"

    logging.info(f"Request received: {request.method} {request.url.path} | Trace ID: {trace_id_hex}")
    response = await call_next(request)
    return response

# Include all the different routers
app.include_router(conversion_routes.router)
app.include_router(job_routes.router)
app.include_router(oracle_routes.router, prefix="/api/oracle")
app.include_router(execution_routes.router, prefix="/api")
app.include_router(migration_routes.router, prefix="/api")

import os

@app.get("/api/default-connection-details/{db_type}", tags=["connection"])
async def get_default_connection_details(db_type: str):
    """Returns default connection details based on the database type."""
    if db_type.lower() == "oracle":
        return {
            "host": os.getenv("ORACLE_DB_HOST", "localhost"),
            "port": int(os.getenv("ORACLE_DB_PORT", "1521")),
            "user": os.getenv("ORACLE_DB_USER", "migrator"),
            "password": os.getenv("ORACLE_DB_PASSWORD", "password"),
            "service_name": os.getenv("ORACLE_DB_SERVICE_NAME", "FREE"),
            "sid": os.getenv("ORACLE_DB_SID", ""),
        }
    elif db_type.lower() == "postgresql":
        return {
            "host": os.getenv("POSTGRES_DB_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_DB_PORT", "5432")),
            "user": os.getenv("POSTGRES_DB_USER", "postgres"),
            "password": os.getenv("POSTGRES_DB_PASSWORD", "postgres"),
            "dbname": os.getenv("POSTGRES_DB_NAME", "postgres"),
        }
    else:
        return {"detail": "Invalid database type"}, 400

@app.get("/health", tags=["health"])
def health_check():
    """A simple health check endpoint."""
    return {"status": "ok"}
