# Environment Setup

Simple environment configuration using `.env` files.

## Required Variables

```bash
# Database connection
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=3306

# Database names
DB_NAME=your_main_database
DB_NAME_TEST=your_test_database
```

## How It Works

- **Main App**: Uses `DB_NAME` and `DATABASE_URL`
- **Tests**: When pytest runs, `DB_NAME` and `DB_NAME_TEST` both point to test database
- **Detection**: Automatically detects pytest via `PYTEST_CURRENT_TEST` environment variable
- **Safety**: Test database names must end with `_test` or start with `test`
- **Shared**: `SERVER_URL` is shared between main and test databases

## Safety Architecture

The system uses a dual-database safety approach:

1. **DB_NAME/DATABASE_URL**: Used by main application logic
2. **DB_NAME_TEST/DATABASE_URL_TEST**: Used by test utilities (safety guarantee)

**When running pytest:**
- `DB_NAME` points to test database (for application logic)
- `DB_NAME_TEST` points to same test database (for test utilities)
- Test utilities ONLY use `DB_NAME_TEST` to guarantee they never touch production

**When not running pytest:**
- `DB_NAME` points to production database
- `DB_NAME_TEST` is `None` (test utilities fail with clear error)

This ensures test utilities can never accidentally operate on production data, even if there are bugs in the pytest detection logic.

## Environment Examples

### Local Development
```bash
DB_USER=local_user
DB_PASSWORD=local_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=qol_local_main
DB_NAME_TEST=qol_local_test
```

### Northflank Dev
```bash
DB_USER=northflank_dev_user
DB_PASSWORD=northflank_dev_password
DB_HOST=northflank_dev_host
DB_PORT=3306
DB_NAME=qol_dev_main
DB_NAME_TEST=qol_dev_test
```

### Northflank Production
```bash
DB_USER=northflank_prod_user
DB_PASSWORD=northflank_prod_password
DB_HOST=northflank_prod_host
DB_PORT=3306
DB_NAME=qol_prod_main
# No DB_NAME_TEST - no testing in production
```

## Running

```bash
# Run tests (DB_NAME points to test database)
pytest

# Run app (DB_NAME points to main database)
python -m app.main
```

## Safety

- Automatic pytest detection prevents manual configuration errors
- Test utilities use dedicated `DB_NAME_TEST` variable (never `DB_NAME`)
- Test database names must end with `_test` or start with `test`
- Test utilities fail with clear error if not running in pytest mode
- Prevents accidental modification of production databases
- `.env` files are ignored by git 