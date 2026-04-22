#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-2}"

exec gunicorn \
  --workers "${WEB_CONCURRENCY}" \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind "0.0.0.0:${PORT}" \
  app.main:app
