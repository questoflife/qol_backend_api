#!/bin/sh
set -e  # Exit on error

ran_any=0

if [ "$RUN_TESTS" = "1" ]; then
  poetry runpytest
  ran_any=1
fi

if [ "$RUN_MAIN" = "1" ]; then
  poetry run python -m app.main
  ran_any=1
fi

if [ "$ran_any" = "0" ]; then
  echo "No action specified. Set RUN_MAIN=1 to run the app, RUN_TESTS=1 to run tests, or both."
  exit 1
fi 