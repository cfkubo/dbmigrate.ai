from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class ConversionInput(BaseModel):
    sql: str
    job_type: str = 'sql'

class ReconversionInput(BaseModel):
    job_id: str
    new_original_sql: Optional[str] = None

class AggregateJobsInput(BaseModel):
    job_ids: List[str]

class OracleConnectionDetails(BaseModel):
    host: str
    port: int
    user: str
    password: str
    service_name: str | None = None
    sid: str | None = None

class PostgresConnectionDetails(BaseModel):
    host: str
    port: int
    user: str
    password: str
    dbname: str

class MigrationCredentials(BaseModel):
    oracle: OracleConnectionDetails
    postgres: PostgresConnectionDetails

class MigrationTableMapping(BaseModel):
    source: str
    destination: str

class DataMigrationRequest(BaseModel):
    oracle_credentials: OracleConnectionDetails
    postgres_credentials: PostgresConnectionDetails
    source_schema: str
    source_table: str
    destination_schema: str
    destination_table: str

class ExtractRequest(BaseModel):
    connection_details: OracleConnectionDetails
    schemas: list[str]
    object_types: list[str]
    object_names: list[str] | None = None
    select_all: bool = False

class ListObjectsRequest(BaseModel):
    connection_details: OracleConnectionDetails
    schema_name: str
    object_type: str

class MigrationObject(BaseModel):
    object_type: str  # e.g., 'TABLE', 'VIEW', 'PROCEDURE', 'FUNCTION', 'INDEX', 'PACKAGE', 'TRIGGER'
    object_name: str

class MigrationDetails(BaseModel):
    source_db_type: str
    target_db_type: str
    source_connection: OracleConnectionDetails
    target_connection: Optional[PostgresConnectionDetails]
    source_schema: str
    target_schema: str # Added target_schema for clarity
    selected_objects: List[MigrationObject]
    data_migration_enabled: bool = False # New flag for data migration

class OracleSchemas(BaseModel):
    schemas: list[str]

class SqlExecutionJob(BaseModel):
    job_id: str
    status: str
    filename: str
    error_message: str | None = None
    submitted_at: str
    processed_at: str | None = None
    statement_results: list[dict] | None = None

class DataMigrationJob(BaseModel):
    job_id: UUID
    source_db_type: str
    source_connection_string: str
    source_table_name: str
    target_db_type: str
    target_connection_string: str
    target_table_name: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_rows: int = 0
    migrated_rows: int = 0
    failed_rows: int = 0
    error_details: Optional[str] = None

class DataMigrationRow(BaseModel):
    row_id: UUID
    job_id: UUID
    source_primary_key_value: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    migrated_at: datetime


class Document(BaseModel):
    id: UUID
    filename: str
    user_id: str
    status: str  # e.g., "processing", "completed", "failed"
    error_message: Optional[str] = None
    created_at: datetime


class DocumentChunk(BaseModel):
    id: UUID
    document_id: UUID
    text: str
    embedding: List[float]

