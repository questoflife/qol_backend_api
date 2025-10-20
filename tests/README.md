# Testing Guide

## Test Types

### Unit Tests (Default)
- `test_database.py` - Database repository operations
- `test_api.py` - API endpoints with mocked authentication
- Always run, no setup needed

### Integration Tests (Optional)
- `test_oauth_integration.py` - Verifies OAuth configuration without browser
- Enable: `RUN_INTEGRATION_TESTS=true`

### E2E Tests (Optional)
- `test_oauth_e2e.py` - Full Discord OAuth flow with real browser automation
- Enable: `RUN_E2E_TESTS=true` + Discord test account credentials
- Uses Playwright in headless mode (no GUI needed in CI/CD)

## E2E Test Flow

1. Opens browser (headless in CI)
2. Navigates to `/login`
3. Logs into Discord with test credentials
4. Authorizes OAuth app
5. Verifies redirect and session cookie
6. Tests authenticated endpoints (`/me`, user dict)
7. Tests logout clears session

## Local Setup

### E2E Tests
```bash
# Install dependencies
poetry install --with testing
playwright install chromium

# Set environment variables
export RUN_E2E_TESTS=true
export DISCORD_TEST_EMAIL=your-test@email.com
export DISCORD_TEST_PASSWORD=your-test-password

# Run tests
pytest tests/test_oauth_e2e.py -v
```

**Important:** Create a dedicated Discord test account. Don't use your personal account (may trigger security alerts).

### Integration Tests
```bash
export RUN_INTEGRATION_TESTS=true
pytest tests/test_oauth_integration.py -v
```

### Run All Tests
```bash
pytest  # Optional tests are skipped unless env vars are set
```

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

## Docker/CI Setup

### Dockerfile
Already configured in `testing` stage:
- Chromium system dependencies (~150MB)
- Playwright browser installation (~150MB)

### Testing Locally with Docker
```bash
# Run all tests
docker compose -p qol-testing \
  -f docker-compose.yml \
  -f dev/docker-compose.prod.db-override.yml \
  run --rm --build testing pytest -v

# Run only E2E tests
docker compose -p qol-testing \
  -f docker-compose.yml \
  -f dev/docker-compose.prod.db-override.yml \
  run --rm --build testing pytest tests/test_oauth_e2e.py -v
```

### Northflank
Everything is configured. Just add secrets:
- `RUN_E2E_TESTS=true`
- `DISCORD_TEST_EMAIL=your-test-discord@email.com`
- `DISCORD_TEST_PASSWORD=your-test-password`

Tests run automatically during build/test phase. E2E tests are skipped unless all three secrets are set.
