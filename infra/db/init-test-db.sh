#!/bin/sh
# Initialize test database with UUID extension
# This script is run after init.sql by Docker's entrypoint

set -e

# Create test database if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE kcardswap_test'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'kcardswap_test')\gexec
EOSQL

# Enable UUID extension in test database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "kcardswap_test" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOSQL

echo "Test database kcardswap_test initialized successfully"
