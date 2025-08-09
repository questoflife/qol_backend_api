# Testing Guide

This project uses pytest as the testing framework, configured through `pytest.ini`. Currently, the only test entrypoint is `pytest`.

## Running Tests

Tests should be run in the testing Docker environment before committing or making pull requests to ensure the codebase is ready for integration. The testing environment mirrors the production setup without development tools, providing the most reliable validation. Local tests in your debug environment may still be useful during development for debugging purposes.

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
