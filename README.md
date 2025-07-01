# Quest of Life Backend API

Async Python/FastAPI service that powers the Quest of Life website.  
Runs on **Northflank**; the static front-end lives on GitHub Pages.

## Backend Functionality
- User key-value storage with user isolation
- Authentication via Discord OAuth2 for api calls (currently mocked for development)


---

## Tech stack

| Layer             | Choice |
| ----------------- | ------ |
| Language          | Python 3.12 |
| Web framework     | FastAPI (async) |
| ASGI server       | Uvicorn |
| ORM / DB driver   | SQLAlchemy 2 (async) |
| Database          | MySQL 8 (Northflank add-on) |
| Dependency mgr    | Poetry |
| Container         | Podman |
| CI / CD           | GitHub Actions → Northflank Pipeline |

---

## Testing

```bash
# Run tests
pytest

# Run specific test
pytest tests/test_database.py::test_create_key_value
```

**Testing & Safety Features:**
- All environment selection is handled via environment variables (see `.env` and `ENVIRONMENT_SETUP.md`).
- The main configuration (`config.py`) is environment-agnostic and reads only from environment variables.
- All test safety and destructive operations are enforced in test utilities and entry points (e.g., `conftest.py`, `database_utils.py`).
- Destructive test operations (e.g., dropping/creating databases) are strictly gated by `APP_ENV=test` and will fail if not in test mode.
- Clean database sessions for each test, robust CRUD, isolation, and concurrency testing.

See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for configuration and environment variable details.

---

## Northflank deployment (free tier)

| Role            | Resource name | Plan             |
| --------------- | ------------- | ---------------- |
| **Live API**    | `api-prod`    | `nf-compute-10` (256 MB) |
| **Staging API** | `api-dev` *¹* | `nf-compute-10` (256 MB) |
| **Database**    | `mysql-qol`   | `nf-compute-20` (512 MB) + 4 GB disk |

> *¹ `api-dev` can be scaled to 0 replicas when you're not actively testing to save costs*

* Only **two** long-running services are allowed on the Developer Sandbox—`api-prod` and `api-dev` use both slots.  
* There is **one** managed add-on (MySQL). **Both services share it, so never run destructive migrations on `api-dev` that could affect prod data.**
