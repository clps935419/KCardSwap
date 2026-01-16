-- KCardSwap Database Initialization Script
-- This script handles database-level setup only.
-- All table schemas are managed by Alembic migrations.

-- Enable UUID extension for main database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: Test database creation is handled by init-test-db.sh
-- This is because PostgreSQL does not allow CREATE DATABASE inside a transaction block
-- and the psql \c command is not available in all execution contexts.

-- Note: All CREATE TABLE and CREATE INDEX statements have been moved to Alembic migrations.
-- Run 'alembic upgrade head' after this script to create the database schema.
