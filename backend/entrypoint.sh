#!/bin/sh
set -e

# Entrypoint para FastAPI
cd /app

echo "Iniciando servidor FastAPI..."

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info