# Quest of Life Backend API

Async FastAPI backend for the Quest of Life website. Provides user key-value storage with user isolation and (mocked) Discord OAuth2 authentication. Runs on Northflank; static frontend is on GitHub Pages.

---

## Quick Start

1. **Set up your `.env` file:**
   ```env
   APP_ENV=dev         # Use 'test' for running tests
   DB_USER=your_user
   DB_PASSWORD=your_password
   DB_HOST=your_host
   DB_PORT=3306
   DB_NAME=your_database  # Use a test DB for tests
   ```
2. **Install dependencies:**
   ```bash
   poetry install
   ```
3. **Run the app:**
   ```bash
   python -m app.main
   ```

**Safety:**
- Destructive operations (e.g., dropping/creating DBs) are only allowed if `APP_ENV=test` and `DB_NAME` points to a test database. This prevents accidental changes to production data.
- `.env` files are git-ignored.

---

## Architecture

```
[API Layer] → [Service/Backend Layer] → [Repository/Database Layer]
```

- **API Layer (`app/api/`)**  
  Handles HTTP requests and responses. Depends on the service/backend layer for business logic.

- **Service/Backend Layer (`app/backend/`)**  
  Contains business logic, orchestration, and validation. Calls repository/database functions to access or modify data.

- **Repository/Database Layer (`app/database/`)**  
  Handles direct database access (CRUD operations, queries). No business logic.

**Example Flow:**
1. API receives a request (e.g., set a user value).
2. API calls the service layer function (e.g., `set_user_key_value`).
3. Service layer may add business logic, then calls the repository function.
4. Repository function interacts with the database.

---

## Tech Stack

| Layer           | Choice                |
| --------------- | --------------------- |
| Language        | Python 3.12           |
| Web framework   | FastAPI (async)       |
| ASGI server     | Uvicorn               |
| ORM / DB driver | SQLAlchemy 2 (async)  |
| Database        | MySQL 8               |
| Dependency mgr  | Poetry                |
| Container       | Podman                |
| CI / CD         | GitHub Actions, Northflank |

---

## Testing

> **⚠️ Never run tests against your production or development database.**
> 
> Before running tests, ensure your `.env` is configured for testing:
> - `APP_ENV=test`
> - `DB_NAME` points to a dedicated test database (e.g., `qol_test`)
> 
> All destructive test operations are strictly gated by these settings, but you must double-check your `.env` to avoid catastrophic data loss.

**How to run tests safely:**
1. Create a `.env` file for testing (or temporarily modify your existing one)
2. Run tests:
   ```bash
   pytest
   ```

