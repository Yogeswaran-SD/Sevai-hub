#!/bin/bash
# Start script for SevaiHub backend

set -e

echo "Starting SevaiHub Backend..."

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Seed database
echo "Seeding database with technician data..."
python seed.py

# Start the application
echo "Starting Uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
