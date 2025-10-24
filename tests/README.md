# Testing Guide

## Test Types

### Unit Tests (Default - Run Locally)
- `test_database.py` - Database repository operations
- `test_api.py` - API endpoints with mocked authentication
- Always run, no setup needed beyond database connection

### Integration Tests (CI/CD)
- `test_oauth_integration.py` - Verifies OAuth configuration
- Tests OAuth endpoints, error handling, session protection, CORS
- Enable: `RUN_INTEGRATION_TESTS=true`

## Local Setup

### Unit Tests
```bash
# Install dependencies
poetry install --with testing

# Run unit tests (database + API)
pytest tests/test_database.py tests/test_api.py -v
```

### Run All Tests
```bash
pytest  # Unit tests always run; integration tests skipped unless RUN_INTEGRATION_TESTS=true
```

## Docker/CI Testing

### Testing Locally with Docker
```bash
# Run all tests (unit tests only by default)
docker compose -p qol-testing \
  -f docker-compose.yml \
  -f dev/docker-compose.prod.db-override.yml \
  run --rm --build testing pytest -v
```

### Northflank
Set these environment variables in Northflank:
- `RUN_INTEGRATION_TESTS=true`
- `FRONTEND_ORIGIN=https://your-app.northflank.app`
- `API_BASE_URL=https://your-app.northflank.app`
- All standard app configuration (Discord OAuth, database, etc.)

Register `https://your-app.northflank.app/oauth/callback` in Discord OAuth app.

## Environment Variables

### Required (All Tests)
Standard app configuration from `src/settings.py`:
- `FRONTEND_ORIGIN`, `API_BASE_URL`
- `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`
- `SECRET_KEY`
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`

### Optional (Integration Tests)
- `RUN_INTEGRATION_TESTS=true`

## CI/CD Setup (Northflank)

Integration tests validate OAuth configuration and endpoint behavior in containerized environments.

**Environment Variables:**
```bash
# Required
FRONTEND_ORIGIN=https://your-app.northflank.app
API_BASE_URL=https://your-app.northflank.app
SECRET_KEY=your-secret-key
DISCORD_CLIENT_ID=your-client-id
DISCORD_CLIENT_SECRET=your-client-secret

# Database
DB_HOST=db
DB_PORT=3306
DB_NAME=qol
DB_USER=root
DB_PASSWORD=your-db-password

# Integration Tests (optional)
RUN_INTEGRATION_TESTS=true
```

**Discord OAuth App Setup:**
Register `https://your-app.northflank.app/oauth/callback` as a redirect URI in your Discord application settings.
