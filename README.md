# Quest of Life Backend API

Async FastAPI backend for the Quest of Life website. Provides user key-value storage with user isolation and (mocked) Discord OAuth2 authentication. Runs on Northflank; static frontend is on GitHub Pages.

---

## Prerequisites

Before you begin, make sure you have the following:

1. **Python 3.12**
   - Download from: https://www.python.org/downloads/release/python-3120/
   - Check installation:
     ```bash
     python --version
     # Should print 3.12.x
     ```

2. **Poetry** (dependency manager)
   - Install (Unix/macOS):
     ```bash
     curl -sSL https://install.python-poetry.org | python3 -
     ```
   - Install (Windows PowerShell):
     ```powershell
     (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
     ```
   - Check installation:
     ```bash
     poetry --version
     ```

3. **MySQL 8** (database server)
   - You need a running MySQL 8+ server.
   - **Quick start with Docker:**
     ```bash
     docker run --name qol-mysql -e MYSQL_ROOT_PASSWORD=rootpw -p 3306:3306 -d mysql:8.4
     ```
   - This starts MySQL 8.4 on port 3306 with user `root` and password `rootpw`.
   - Connect using: host `localhost`, port `3306`, user `root`, password `rootpw`.

---

## Quick Start

1. **Set up your `.env` file (must point to your MySQL database):**
   ```env
   APP_ENV=test         # Use 'test' for running tests, 'prod' for deployment
   DB_USER=root
   DB_PASSWORD=rootpw
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=qol_db_test  # Use a test DB for tests
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

## Developer Configuration

This project supports developer-specific configurations that won't affect other team members:

1. **Application Settings**: Create `config/app.env` from `config/app.env.example` (optional)
2. **Database Settings**: Create `config/db.env` from `config/db.env.example` (required for database profiles)
3. **Developer Overrides**: Create `config/dev.env` from `config/dev.env.example` (optional)
4. **Build Dependencies**: Create `config/apt-build-packages.txt` from `config/apt-build-packages.txt.example` (optional)
5. **Runtime Tools**: Create `config/apt-runtime-packages.txt` from `config/apt-runtime-packages.txt.example` (optional)
6. **Python Packages**: Create `config/python-dev-packages.txt` from `config/python-dev-packages.txt.example` (optional)

All these files are gitignored for your personal configuration.

See [Developer Configuration Guide](./docs/DEVELOPER_CONFIG.md) for detailed instructions.

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

## Docker Development

This project includes a multi-stage Dockerfile that supports different development scenarios:

### Docker Image Types

1. **Production (`prod`)**: Minimal image with only production dependencies
2. **Testing (`testing`)**: Image with test dependencies for running automated tests
3. **Development (`dev`)**: Customizable development environment with developer tools

### Using Development Docker Environment

To create a customized development environment:

1. **Configure your development packages**:
   - Copy `.devpackages.example` to `.devpackages` and uncomment/add the Python packages you need
   - Copy `.dev-apt-build-packages.example` to `.dev-apt-build-packages` for build-time dependencies
   - Copy `.dev-apt-runtime-packages.example` to `.dev-apt-runtime-packages` for runtime development tools

2. **Build and run the development container**:
   ```bash
   # Build development image with your custom packages
   docker build -t qol-backend-dev --target dev .

   # Run container with local code mounted
   docker run -it --name qol-dev -p 8080:8080 -v $(pwd):/qol_backend_api qol-backend-dev
   ```

3. **Access the development environment**:
   ```bash
   # If your container is stopped, start it
   docker start qol-dev

   # Access a shell in the container
   docker exec -it qol-dev bash
   ```

4. **Run the development server**:
   ```bash
   # Inside the container
   python -m src.app
   ```

### Benefits of Docker Development

- Consistent environment across all team members
- Easy to add custom development tools without affecting the team
- Isolated from your local system dependencies
- Same environment as CI/CD pipelines for better testing
- Quick reset by rebuilding the container

