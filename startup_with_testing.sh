#!/bin/bash
set -e  # Exit immediately if a command exits with non-zero status

echo "==== Running tests ===="
pytest "$@"

echo "==== Tests passed. Starting server ===="
exec python -m uvicorn src.app:app --host 0.0.0.0 --port 8000
