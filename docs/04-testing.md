# Testing Guide

This document explains how to run tests and the philosophy behind the testing setup.

## Running Tests

The most reliable way to run the entire test suite is by using the `testing` profile in Docker Compose.

```bash
docker compose --profile testing up --build
```

This command does the following:
1.  Builds the `testing` stage of the `Dockerfile`, which includes all testing dependencies.
2.  Spins up a dedicated `testing-db` service, a fresh MySQL instance configured just for this test run.
3.  Runs the `pytest` command inside the test container against the test database.
4.  The services are torn down after the tests complete.

This ensures that tests are always run in a clean, isolated, and consistent environment, preventing issues like data contamination between test runs.

## Test Database

The `testing-db` service is ephemeral. It is created when you run the tests and destroyed afterward. The database schema is created and populated by the tests themselves, ensuring that the tests control their own state.

**⚠️ Never run tests against a development or production database.** The testing setup is designed to prevent this, but always be mindful of your environment configuration.

## Writing Tests

-   **Location:** All tests are located in the `tests/` directory.
-   **Fixtures:** Common test setup and utilities are located in `tests/conftest.py`. This includes fixtures for creating a test database session and a test API client.
-   **Naming:** Test files should be named `test_*.py`, and test functions should be named `test_*`.
-   **Assertions:** Use the standard `assert` statement provided by `pytest`.

### Example Test

```python
# tests/test_api.py

from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```
