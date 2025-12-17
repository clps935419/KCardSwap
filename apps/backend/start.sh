#!/bin/bash
set -e

# Configure Poetry not to create virtualenvs inside container
poetry config virtualenvs.create false

echo "Installing dependencies..."
poetry install --no-root --only main

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
if [ "${ENVIRONMENT:-}" = "development" ] || [ "${DEBUG:-}" = "true" ]; then
  echo "Starting application (development mode) with reload..."
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app/app
else
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
