# Environment Setup

Simple environment configuration using `.env` files.

## Required Variables

```bash
# Environment
APP_ENV=dev  # Set to 'test' for running tests and destructive operations

# Database connection
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=3306

# Database name
DB_NAME=your_database  # Should be a test database when running tests
```

## How It Works

- **Main App**: Uses `DB_NAME` and `DATABASE_URL` for all environments.
- **Tests**: When running tests, set `APP_ENV=test` and `DB_NAME` to your test database.
- **Safety**: All destructive test operations are strictly gated by `APP_ENV=test` and will fail otherwise.
- **Shared**: `SERVER_URL` is shared between main and test databases.

## Safety Architecture

The system uses a robust, environment-driven safety approach:

- `DB_NAME` is used for all environments. When running tests, it must point to a dedicated test database.
- `APP_ENV` controls the environment mode. Destructive operations are only allowed when `APP_ENV=test`.
- For extra safety, some test utilities may use `DB_NAME_TEST` if present, but it is not required.

**When running tests:**
- `APP_ENV` must be set to `test`.
- `DB_NAME` must point to a test database (e.g., ending with `_test` or starting with `test`).
- All destructive operations are gated by these checks.

**When not running tests:**
- `APP_ENV` should be set to `dev` or `prod` as appropriate.
- `DB_NAME` points to the main or production database.
- Destructive test utilities will fail if `APP_ENV` is not `test`.

This ensures test utilities can never accidentally operate on production data, even if there are bugs in the environment detection logic.


## Running

```bash
# Run tests (DB_NAME points to test database, APP_ENV must be 'test')
pytest

# Run app (DB_NAME points to main database, APP_ENV should be 'dev' or 'prod')
python -m app.main
```

## Safety

- All destructive test operations are strictly gated by `APP_ENV=test` and will fail otherwise.
- The `DB_NAME` variable is used for all environments; when running tests, it must point to a dedicated test database.
- Test utilities and fixtures enforce all safety; `config.py` is environment-agnostic and never contains test-specific logic.
- Prevents accidental modification of production databases.
- `.env` files are ignored by git 