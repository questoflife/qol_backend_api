# Testing Guide

This project uses pytest as the testing framework, configured through `pytest.ini`.

### Option A: External Database Testing

**Run Tests Only (Recommended):**
```bash
docker compose run testing pytest
```
Runs pytest in the production Docker environment for the most reliable test results.

**Run Tests + Launch API:**
```bash
docker compose up testing
```
Runs pytest first, then launches the app for manual integration testing if pytest passes successfully (uses `startup_with_testing.sh`).

### Option B: Database in Docker Testing

**Run Tests Only (Recommended):**
```bash
docker compose -f docker-compose.yml -f dev/docker-compose.prod.db-override.yml run testing pytest
```
Runs pytest in the production Docker environment with database override for the most reliable test results.

**Run Tests + Launch API:**
```bash
docker compose -f docker-compose.yml -f dev/docker-compose.prod.db-override.yml up testing
```
Runs pytest first, then launches the app for manual integration testing if pytest passes successfully (uses `startup_with_testing.sh`).

**VS Code:**
- Use command palette: `Tasks: Run Test Task` (runs the appropriate docker compose command)
- Or run pytest natively in the dev environment for debugging

## Test Framework

- **Framework:** pytest with isolated test database instances
- **Environment:** Tests run in production Docker environment for reliability
- **Coverage:** Comprehensive test coverage for the user key-value storage API, including basic functionality, concurrency testing, and error handling scenarios
