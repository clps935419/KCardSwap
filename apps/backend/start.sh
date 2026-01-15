#!/bin/bash
set -e

# Configure Poetry not to create virtualenvs inside container
poetry config virtualenvs.create false

echo "Installing dependencies..."
poetry install --no-root --only main

echo "Running database migrations on main database..."
alembic upgrade head

# Run migrations on test database if TEST_DATABASE_URL is set
if [ -n "${TEST_DATABASE_URL:-}" ]; then
  echo "Running database migrations on test database..."
  DATABASE_URL="$TEST_DATABASE_URL" alembic upgrade head
fi

# Initialize default admin user if configured
if [ "${INIT_DEFAULT_ADMIN:-}" = "true" ]; then
  echo "Initializing default admin user..."
  python scripts/init_admin.py --quiet || echo "Warning: Failed to initialize admin (may already exist)"
fi

echo "Starting application..."
if [ "${ENVIRONMENT:-}" = "development" ] || [ "${DEBUG:-}" = "true" ]; then
  echo "Starting application (development mode) with reload..."
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app/app
else
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
