#!/bin/sh
set -e

echo "🚀 Starting CareerOS 2.0 Cloud Run Service..."

PORT="${PORT:-8080}"
BACKEND_PORT="8000"

echo "⚙️ Initializing SQLite WAL schema migrations..."
python -c "from engine.storage.migrator import run_migrations; run_migrations()"

echo "🐍 Launching FastAPI Backend on internal port ${BACKEND_PORT}..."
python careeros_cli.py server --port ${BACKEND_PORT} --host 127.0.0.1 &
BACKEND_PID=$!

echo "⏳ Awaiting backend readiness..."
for i in $(seq 1 30); do
  if curl -s http://127.0.0.1:${BACKEND_PORT}/health > /dev/null 2>&1; then
    echo "✅ FastAPI Backend is ready!"
    break
  fi
  sleep 0.5
done

echo "⚛️ Launching Next.js Standalone Frontend on Cloud Run port ${PORT}..."
export PORT="${PORT}"
export BACKEND_INTERNAL_URL="http://127.0.0.1:${BACKEND_PORT}/api/:path*"

exec node /app/frontend-server/server.js