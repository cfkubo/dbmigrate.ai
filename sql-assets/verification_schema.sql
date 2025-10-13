CREATE DATABASE verification_db;
CREATE USER verification_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE verification_db TO migration_jobs;
