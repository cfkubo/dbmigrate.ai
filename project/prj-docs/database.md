# Database Documentation

This document provides an overview of the PostgreSQL database usage in the SPF Converter application.

## PostgreSQL Usage

The application uses a PostgreSQL database to manage the asynchronous conversion of stored procedures. When a user submits a stored procedure for conversion, a new job is created and stored in the database. A background worker process picks up pending jobs from the database, performs the conversion, and updates the job status with the result.

The application connects to the database using the `psycopg2` library. Connection parameters are configured through environment variables.

## Tables

The database consists of a single table: `jobs`.

### `jobs` table

This table stores information about each conversion job.

| Column          | Type    | Description                                                                 |
|-----------------|---------|-----------------------------------------------------------------------------|
| `job_id`        | UUID    | The primary key for the table. A unique identifier for each conversion job. |
| `status`        | TEXT    | The current status of the job. Possible values are 'pending', 'completed', 'failed'. |
| `job_type`      | TEXT    | The type of job. For example, 'spf' for stored procedure conversion.        |
| `original_sql`  | TEXT    | The original SQL code of the stored procedure submitted for conversion.     |
| `converted_sql` | TEXT    | The converted PostgreSQL code. This is populated when the job is completed successfully. |
| `error_message` | TEXT    | Any error message that occurred during the conversion process. This is populated when the job fails. |

## Relationships

There is only one table in the database, so there are no relationships between tables.
