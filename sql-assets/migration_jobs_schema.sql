DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'migration_jobs') THEN

      CREATE ROLE migration_jobs WITH LOGIN PASSWORD 'password';
   END IF;
END
$do$;
ALTER ROLE migration_jobs WITH SUPERUSER;

CREATE SCHEMA IF NOT EXISTS migration_jobs;

CREATE TABLE IF NOT EXISTS migration_jobs.jobs (
    job_id UUID PRIMARY KEY,
    parent_job_id UUID,
    status TEXT NOT NULL,
    job_type TEXT NOT NULL,
    original_sql TEXT NOT NULL,
    converted_sql TEXT,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    source_db_type TEXT,
    target_db_type TEXT,
    source_connection_details JSONB,
    target_connection_details JSONB,
    source_schema TEXT,
    target_schema TEXT,
    object_type TEXT,
    object_name TEXT,
    data_migration_enabled BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (parent_job_id) REFERENCES migration_jobs.jobs(job_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS migration_jobs.data_migration_jobs (
    job_id UUID PRIMARY KEY,
    status TEXT NOT NULL,
    source_db_type TEXT NOT NULL,
    source_connection_string TEXT NOT NULL,
    source_schema_name TEXT NOT NULL,
    source_table_name TEXT NOT NULL,
    target_db_type TEXT NOT NULL,
    target_connection_string TEXT NOT NULL,
    target_schema_name TEXT NOT NULL,
    target_table_name TEXT NOT NULL,
    total_rows INTEGER DEFAULT 0,
    migrated_rows INTEGER DEFAULT 0,
    error_details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS migration_jobs.sql_execution_jobs (
    job_id UUID PRIMARY KEY,
    status TEXT NOT NULL,
    filename TEXT NOT NULL,
    sanitized_sql TEXT,
    error_message TEXT,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    processed_at TIMESTAMP WITH TIME ZONE,
    statement_results JSONB
);
