# Testing Guide

## Test Types

### Unit Tests (Default - Run Locally)
- `test_database.py` - Database repository operations
- `test_api.py` - API endpoints with mocked authentication
- Always run, no setup needed beyond database connection

### Integration Tests (CI/CD Only)
- `test_oauth_integration.py` - Verifies OAuth configuration without browser
- Enable: `RUN_INTEGRATION_TESTS=true`

### E2E Tests (CI/CD Only)
- `test_oauth_e2e.py` - Full Discord OAuth flow with browser automation
- Enable: `RUN_E2E_TESTS=true` + Discord test account credentials
- Uses Playwright with headless Chromium (no GUI needed)

**Note:** E2E and integration tests are designed to run on Northflank, not locally.

## E2E Test Flow (Northflank)

1. Starts server in container (headless Chromium, no GUI)
2. Browser navigates to `/login`
3. Logs into Discord with test credentials
4. Authorizes OAuth app
5. Verifies redirect and session cookie
6. Tests authenticated endpoints (`/me`, user dict)
7. Tests logout clears session

## Local Setup

### Unit Tests Only
```bash
# Install dependencies
poetry install --with testing

# Run unit tests (database + API)
pytest tests/test_database.py tests/test_api.py -v
```

**Note:** E2E and integration tests are not designed for local development.

### Run All Tests
```bash
pytest  # Unit tests always run; E2E/integration skipped unless env vars set
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
- `RUN_E2E_TESTS=true`
- `DISCORD_TEST_EMAIL=your-test-discord@email.com`
- `DISCORD_TEST_PASSWORD=your-test-password`
- `FRONTEND_ORIGIN=https://your-app.northflank.app`
- `API_BASE_URL=https://your-app.northflank.app`

Register `https://your-app.northflank.app/oauth/callback` in Discord OAuth app.

Tests run automatically during build/test phase. E2E tests are skipped unless all required env vars are set.

## Environment Variables

### Required (All Tests)
Standard app configuration from `src/settings.py`:
- `FRONTEND_ORIGIN`, `API_BASE_URL`
- `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`
- `SECRET_KEY`
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`

### Optional (Integration Tests)
- `RUN_INTEGRATION_TESTS=true`

### Optional (E2E Tests)
- `RUN_E2E_TESTS=true`
- `DISCORD_TEST_EMAIL` - Test Discord account email
- `DISCORD_TEST_PASSWORD` - Test Discord account password

## CI/CD Setup (Northflank)

E2E and integration tests run in containerized environments. The E2E tests start their own server on `0.0.0.0:8000` and use Chromium for browser automation.

### Northflank Configuration

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

# E2E Tests (optional)
RUN_E2E_TESTS=true
DISCORD_TEST_EMAIL=your-test-discord@email.com
DISCORD_TEST_PASSWORD=your-test-password
```

**Discord OAuth App Setup:**
Register `https://your-app.northflank.app/oauth/callback` as a redirect URI in your Discord application settings.

**How It Works:**
1. Tests start a server on `0.0.0.0:8000` inside the container
2. Browser navigates to `API_BASE_URL` (public Northflank URL)
3. OAuth flow redirects to Discord and back to your callback
4. Tests verify session management and API functionality
5. If tests pass, main server can start (future enhancement)
