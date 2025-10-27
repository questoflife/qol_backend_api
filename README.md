# Quest of Life Backend API

This is a REST API for a backend and database to the Quest of Life website.

Currently the app can only be run on a single server, not parallel. Redis would have to be implemented for that to be possible (for rate limiter).

# Setup
## Production
**Prerequisites:** Docker 20.10+, MySQL 8 database

- Run a MySQL 8 database in your preferred manner.
- Prepare the environment variables as per specification in `.devcontainer/.env.example`.
- Build and run the Dockerfile `prod` stage with its default entrypoint (with env vars from *step 2*)

**For testing:** build and run the Dockerfile `testing` stage instead. It will first run its tests. If all tests pass, it will launch the app.

## Development and Local Testing
**Prerequisites:** Docker 20.10+, Docker Compose 2.24+

**Step 1:** Copy `.devcontainer/.env.example` to `.devcontainer/.env` and modify accordingly (see comments in the file and section **Env Variables**)

*The project is configured to launch a MySQL 8 Database in a docker container explicitly for this app only. Choose one of the following three sections depending on what setup you want:*
### Option 1: In VS Code, in container, with database: (Recommended) 
**For Development:** Open project in container (Dockerfile `dev` stage with MySQL `db` container)

**For Testing** Run VS code test task (Dockerfile `test` stage running tests only, with MySQL `db` container)


### Option 2: Using docker-compose directly, with database
**For Development:** `docker compose -f .devcontainer/docker-compose.dev-with-db.yml up`

**For Testing** `docker compose -f .devcontainer/docker-compose.test-with-db.yml run --rm --build testing; docker compose -f .devcontainer/docker-compose.test-with-db.yml down`


### Option 3: Using docker-compose directly, without database
*Make sure to set up your own MySQL 8 Database and provide its credentials appropriately in `.devcontainer/.env`*
**For Development:** `docker compose -f .devcontainer/docker-compose.dev.yml up`

**For Testing** `docker compose -f .devcontainer/docker-compose.test.yml run --rm --build testing`

# Documentation
Find documentation in the `docs` directory

### Tech Stack
| Layer           | Choice                |
| --------------- | --------------------- |
| Language        | Python 3.12           |
| Web framework   | FastAPI (async)       |
| ASGI server     | Uvicorn               |
| ORM / DB driver | SQLAlchemy 2 (async)  |
| Database        | MySQL 8               |
| Dependency mgr  | Poetry                |
| Container       | Docker                |

# TODO
SECURITY.md
Proper versioning practice with CHANGELOG.md for initial realease
LICENSE & CONTRIBUTING.md