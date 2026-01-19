#!/bin/sh
set -e

if [ -z "${POSTGRES_USER:-}" ] || [ -z "${POSTGRES_PASSWORD:-}" ]; then
  echo "POSTGRES_USER or POSTGRES_PASSWORD is not set"
  exit 1
fi

export PGPASSWORD="$POSTGRES_PASSWORD"

ensure_db() {
  db_name="$1"
  exists=$(psql -h db -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='${db_name}'")
  if [ "$exists" != "1" ]; then
    echo "Creating database ${db_name}..."
    psql -h db -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE ${db_name};"
  else
    echo "Database ${db_name} already exists"
  fi
}

ensure_extension() {
  db_name="$1"
  echo "Ensuring uuid-ossp on ${db_name}..."
  psql -h db -U "$POSTGRES_USER" -d "$db_name" -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
}

ensure_db "kcardswap_test"
ensure_extension "kcardswap"
ensure_extension "kcardswap_test"

echo "Database initialization checks completed"
