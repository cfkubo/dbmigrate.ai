import psycopg2
import psycopg2.extras
from psycopg2 import pool
import uuid
import os
import redis
import logging
from contextlib import contextmanager
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

psycopg2.extras.register_uuid()

# Initialize Valkey client
valkey_client = redis.Redis(host='localhost', port=6379, db=0)

db_pool = None
verification_db_pool = None
rag_db_pool = None

def initialize_db_pool():
    global db_pool
    if db_pool is None:
        logger.info("Initializing main database connection pool...")
        logger.info(f"DB_HOST: {os.getenv('POSTGRES_HOST')}, DB_PORT: {os.getenv('POSTGRES_PORT')}, DB_NAME: {os.getenv('APP_POSTGRES_DB')}")
        db_pool = pool.SimpleConnectionPool(
            1, 20, # minconn, maxconn
            dbname=os.getenv("APP_POSTGRES_DB", "migration_jobs"),
            user=os.getenv("APP_POSTGRES_USER", "migration_jobs"),
            password=os.getenv("APP_POSTGRES_PASSWORD", "password"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
        )

def initialize_verification_db_pool():
    global verification_db_pool
    if verification_db_pool is None:
        logger.info("Initializing verification database connection pool...")
        verification_db_pool = pool.SimpleConnectionPool(
            1, 5, # minconn, maxconn - verification might need fewer connections
            dbname=os.getenv("VERIFICATION_DB_NAME", "verification_db"),
            user=os.getenv("VERIFICATION_DB_USER", os.getenv("POSTGRES_USER", "postgres")),
            password=os.getenv("VERIFICATION_DB_PASSWORD", os.getenv("POSTGRES_PASSWORD", "postgres")),
            host=os.getenv("VERIFICATION_DB_HOST", os.getenv("POSTGRES_HOST", "localhost")),
            port=os.getenv("VERIFICATION_DB_PORT", os.getenv("POSTGRES_PORT", "5432")),
        )

def initialize_rag_db_pool():
    global rag_db_pool
    if rag_db_pool is None:
        logger.info("Initializing RAG database connection pool (migrateaidb)...")
        rag_db_pool = pool.SimpleConnectionPool(
            1, 10, # minconn, maxconn - RAG might need a moderate number of connections
            dbname=os.getenv("RAG_POSTGRES_DB", "migrateaidb"),
            user=os.getenv("RAG_POSTGRES_USER", "migrateaidb"),
            password=os.getenv("RAG_POSTGRES_PASSWORD", "password"),
            host=os.getenv("RAG_POSTGRES_HOST", "localhost"),
            port=os.getenv("RAG_POSTGRES_PORT", "5432"),
        )

@contextmanager
def get_db_connection():
    """Gets a connection from the main database pool and sets it to autocommit."""
    if db_pool is None:
        initialize_db_pool()
    conn = db_pool.getconn()
    conn.autocommit = True
    try:
        yield conn
    finally:
        db_pool.putconn(conn)

@contextmanager
def get_verification_db_connection():
    """Gets a connection from the verification database pool."""
    if verification_db_pool is None:
        initialize_verification_db_pool()
    conn = verification_db_pool.getconn()
    try:
        yield conn
    finally:
        verification_db_pool.putconn(conn)

@contextmanager
def get_rag_db_connection():
    """Gets a connection from the RAG database pool (migratedbai)."""
    if rag_db_pool is None:
        initialize_rag_db_pool()
    conn = rag_db_pool.getconn()
    try:
        yield conn
    finally:
        rag_db_pool.putconn(conn)

@contextmanager
def get_db_connection_by_db_name(dbname: str, user: Optional[str] = None, password: Optional[str] = None, host: Optional[str] = None, port: Optional[str] = None):
    """Gets a connection to a specific database, creating a temporary pool if necessary."""
    
    # Use provided credentials or fallback to environment variables
    db_user = user if user is not None else os.getenv("POSTGRES_USER", "migration_jobs")
    db_password = password if password is not None else os.getenv("POSTGRES_PASSWORD", "password")
    db_host = host if host is not None else os.getenv("POSTGRES_HOST", "localhost")
    db_port = port if port is not None else os.getenv("POSTGRES_PORT", "5432")

    temp_pool = None
    conn = None
    try:
        # Create a simple, temporary connection pool for this specific database
        temp_pool = psycopg2.pool.SimpleConnectionPool(
            1, 1,
            dbname=dbname,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        conn = temp_pool.getconn()
        yield conn
    finally:
        if conn:
            temp_pool.putconn(conn)
        if temp_pool:
            temp_pool.closeall()

def _convert_uuids_to_strings(data):
    if isinstance(data, dict):
        return {k: _convert_uuids_to_strings(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_convert_uuids_to_strings(i) for i in data]
    if isinstance(data, uuid.UUID):
        return str(data)
    return data
