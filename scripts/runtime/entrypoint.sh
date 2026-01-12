#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${MNEMOSYS_ENV:-}" ]]; then
  echo "ERROR: MNEMOSYS_ENV is required." >&2
  exit 2
fi

echo "Running Alembic migration gate..."
python /app/alembic/runner.py upgrade

uvicorn_args=(
  "mnemosys_core.api.runtime:create_application"
  --factory
  --host "0.0.0.0"
  --port "${UVICORN_PORT:-8000}"
  --proxy-headers
)

if [[ -n "${UVICORN_WORKERS:-}" ]]; then
  uvicorn_args+=(--workers "${UVICORN_WORKERS}")
fi

exec uvicorn "${uvicorn_args[@]}"
