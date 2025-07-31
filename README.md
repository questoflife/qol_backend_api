# Quest of Life Backend API

Async FastAPI backend for the Quest of Life website.

This repository contains a Python backend service that exposes a REST API and connects to a MySQL database. It handles user data storage and retrieval for the Quest of Life website.

## Tech Stack

| Layer           | Choice                |
| --------------- | --------------------- |
| Language        | Python 3.12           |
| Web framework   | FastAPI (async)       |
| ASGI server     | Uvicorn               |
| ORM / DB driver | SQLAlchemy 2 (async)  |
| Database        | MySQL 8               |
| Dependency mgr  | Poetry                |
| Container       | Docker                |

## Quick Start

> **Note:** This is for production setup only. For development instructions, see the [Installation Guide](docs/01-installation.md).

### Prerequisites
- Docker and Docker Compose
- MySQL 8 database

### Production Setup
1. **Configure environment:**
   ```bash
   cp app.env.example app.env
   ```
   Fill in your database credentials in `app.env`.

2. **Run:**
   ```bash
   docker compose up
   ```

3. **Test:**
   ```bash
   docker compose run testing pytest
   ```

## Documentation

For detailed setup, development, and testing instructions, see:

- **[Installation Guide](docs/01-installation.md)** - Complete setup instructions for production and development
- **[Configuration Guide](docs/02-configuration.md)** - Environment variables and configuration
- **[Architecture Guide](docs/03-architecture.md)** - Codebase structure and API endpoints
- **[Testing Guide](docs/04-testing.md)** - Running tests and test framework details
- **[Development Guide](docs/05-development-guide.md)** - Development workflow and coding standards
