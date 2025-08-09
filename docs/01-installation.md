# Installation Guide

This guide provides comprehensive setup instructions for both production and development environments.

## Prerequisites

- Docker
- Docker Compose
- MySQL 8 database

## Quick Start (Production)

1. **Clone the repository and navigate to the project directory:**

2. **Configure environment:**
    ```bash
    cp app.env.example app.env
    ```
    Fill in the database credentials in `app.env` based on `app.env.example` to specify how the backend connects to your MySQL database.

3. **Run with Docker Compose:**
    ```bash
    docker compose up
    ```

### Testing

Run tests to verify the setup (from the project directory):
```bash
docker compose run testing pytest
```

## Development Setup

The `dev_example` directory is committed to git and contains an example configuration and Docker files. Copy its contents to the repository root; the resulting paths (for example, `dev/`) are gitignored so you can customize them locally. Edit files inside `dev_example` only if you want to update the shared templates in the repository.

**Copy local configuration templates:**
```bash
cp -r dev_example/* .
```

Tips:
- To avoid overwriting existing local changes: `cp -rn dev_example/* .`
- To refresh with the latest templates (overwrite): `cp -r dev_example/* .`

---

#### 
> **Quick start:** For the simplest recommended setup, skip to [Option B → B3. VS Code Integrated Docker](#vs-code-integrated-docker--recommended---simplest-setup).

### Option A: External Database (you host elsewhere)

**Configure database connection:**
- Fill in `dev/dev.env` with your database credentials.

**Choose your preferred development method and follow one of {A1, A2}:**

- **Option A1: For development with custom local Python** (Prerequisites: Python 3.12+ and Poetry)
    Use your own local environment with at least the requirements listed in pyproject.toml.
    
    Load environment variables (see [Configuration Guide](../docs/02-configuration.md#loading-environment-variables)) then:
    - **Run the app:** `python -m uvicorn src.app:app --host 0.0.0.0 --port 8000`
    - **Run tests:** `pytest`
    - **Debug/develop:** Use your IDE or run individual Python modules

- **Option A2: For Docker Containerization**

    Build the development container and its dependencies:
    ```bash
    docker compose -f dev/docker-compose.dev.yml build --with-dependencies dev
    ```

    Alternatively, build dependencies manually first:
    ```bash
    docker compose -f dev/docker-compose.dev.yml build runtime-base testing-builder
    docker compose -f dev/docker-compose.dev.yml build dev
    ```

    Run commands in isolation (creates and destroys container):
    ```bash
    docker compose -f dev/docker-compose.dev.yml run dev python
    ```

    Start persistent container for faster repeated access:
    ```bash
    # Start container
    docker compose -f dev/docker-compose.dev.yml up -d dev

    # Execute commands in running container
    docker compose -f dev/docker-compose.dev.yml exec dev python
    ```

### Option B: Database in Docker

**Configure database settings:**
- Modify `dev/db.env` according to your preferences

**Choose your preferred development method and follow one of {B1, B2, B3}:**

- **Option B1: For development with custom local Python** (Prerequisites: Python 3.12+ and Poetry)
    Start database only:
    ```bash
    docker compose -f dev/docker-compose.dev.yml -f dev/docker-compose.dev.db-override.yml up db
    ```
    Then use your own local environment with at least the requirements listed in pyproject.toml.
    
    Load environment variables (see [Configuration Guide](../docs/02-configuration.md#loading-environment-variables)) then:
    - **Run the app:** `python -m uvicorn src.app:app --host 0.0.0.0 --port 8000`
    - **Run tests:** `pytest`
    - **Debug/develop:** Use your IDE or run individual Python modules

- **Option B2: For Docker Containerization**

    Build the development container and its dependencies:
    ```bash
    docker compose -f dev/docker-compose.dev.yml -f dev/docker-compose.dev.db-override.yml build --with-dependencies dev
    ```

    Alternatively, build dependencies manually first:
    ```bash
    docker compose -f dev/docker-compose.dev.yml build runtime-base testing-builder
    docker compose -f dev/docker-compose.dev.yml -f dev/docker-compose.dev.db-override.yml build dev
    ```

    Run commands in isolation (creates and destroys container):
    ```bash
    docker compose -f dev/docker-compose.dev.yml -f dev/docker-compose.dev.db-override.yml run dev python
    ```

    Start persistent container for faster repeated access:
    ```bash
    # Start container
    docker compose -f dev/docker-compose.dev.yml -f dev/docker-compose.dev.db-override.yml up -d dev

    # Execute commands in running container
    docker compose -f dev/docker-compose.dev.yml -f dev/docker-compose.dev.db-override.yml exec dev python
    ```

- **Option B3: VS Code Integrated Docker** ⭐ **Recommended - Simplest Setup**

    The `.devcontainer` configuration prepares everything automatically including the database and development environment.
    
    - Open the project folder in VS Code
    - Use command palette: `Dev Containers: Reopen in Container`
    - VS Code will build and start the complete development environment

## Offline Preparation

For environments with limited or no internet access, you can pre-build and cache all Docker images:

```bash
./dev/prepare-offline.sh
```

This script builds and downloads all Docker images and dependencies, including:
- Base Python images
- Development and testing containers  
- Production containers
- Database containers

Required for VS Code dev container integration when working offline.
