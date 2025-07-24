# Configuration Guide

This document explains how environment variables and developer-specific configurations work in this project.

## Environment Variables

The application's configuration is managed through `.env` files located in the `config/` directory. This allows for a flexible setup where different environments (development, testing, production) can have different settings.

### Configuration Files

-   `config/app.env`: Base application settings. Loaded by all services.
-   `config/db.env`: Database connection settings. Used by `dev-db` and `testing-db` services to automatically configure the database.
-   `config/dev.env`: Developer-specific overrides. Loaded only in the `dev` profile, and its values take precedence over `app.env`.

### Precedence Order

The environment files are loaded in a specific order, with later files overriding earlier ones:
1.  `config/app.env` (Lowest priority)
2.  `config/db.env`
3.  `config/dev.env` (Highest priority)

### `db.env` for Local Databases

The `docker-compose.yml` is configured to use `config/db.env` to set up the MySQL databases for local development and testing.

-   The `dev-db` service uses it to create and configure the development database.
-   The `testing-db` service uses it to create and configure the test database.

This means you don't have to manually create databases or users. Just configure `config/db.env` and `docker-compose` handles the rest.

## Customizing Your Development Environment

The development container is designed to be customizable without affecting the project's core dependencies.

### Adding Python Packages

To add personal Python tools (e.g., `ipython`, `httpie`):
1.  Create `config/python-dev-packages.txt` if it doesn't exist.
2.  Add one package name per line.
3.  Rebuild the dev container: `docker compose --profile dev-db up --build`

### Adding System Packages

To add system-level tools (e.g., `vim`, `htop`):
1.  **Build-time dependencies:** Add to `config/apt-build-packages.txt` (for compiling Python packages).
2.  **Runtime tools:** Add to `config/apt-runtime-packages.txt` (for interactive use).
3.  Rebuild the dev container.
