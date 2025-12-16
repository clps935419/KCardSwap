#!/bin/bash
set -e

echo "Installing dependencies..."
poetry config virtualenvs.create false
poetry install --no-root --only main

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
