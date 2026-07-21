#!/usr/bin/env bash
# start.sh — used by Render as the startCommand
# 1. Seed the database with any missing tables
# 2. Start the FastAPI server
set -e

echo "==> Running database seed..."
python -m backend.seed

echo "==> Starting uvicorn on port ${PORT:-8000}..."
exec uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8000}"
