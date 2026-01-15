-- KCardSwap Database Initialization Script
-- This script handles database-level setup only.
-- All table schemas are managed by Alembic migrations.

-- Enable UUID extension for main database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create test database
SELECT 'CREATE DATABASE kcardswap_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'kcardswap_test')\gexec

-- Connect to test database and enable UUID extension
\c kcardswap_test
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Switch back to main database
\c kcardswap

-- Note: All CREATE TABLE and CREATE INDEX statements have been moved to Alembic migrations.
-- Run 'alembic upgrade head' after this script to create the database schema.
