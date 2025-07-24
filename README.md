# Quest of Life Backend API

Async FastAPI backend for the Quest of Life website. Provides user key-value storage with user isolation and (mocked) Discord OAuth2 authentication.

## Features

-   **FastAPI Backend:** Modern, fast, and asynchronous web framework.
-   **User Data Storage:** Simple key-value storage for user-specific data.
-   **Dockerized Environment:** Consistent development, testing, and production environments with Docker and Docker Compose.
-   **VS Code Dev Container:** Pre-configured development environment for a seamless start.
-   **Layered Architecture:** Clear separation of concerns between API, business logic, and data access layers.

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
| CI / CD         | GitHub Actions        |

## Prerequisites

-   [Docker Desktop](https://www.docker.com/products/docker-desktop/)
-   [Visual Studio Code](https://code.visualstudio.com/)
-   [VS Code Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## Quick Start

The best way to get started is with the VS Code Dev Container.

1.  **Clone the repository.**
2.  **Open the project folder in VS Code.**
3.  Click **"Reopen in Container"** when prompted.
4.  Once the container is built, run the development server with the database:
    ```bash
    docker compose --profile dev-db up --build
    ```
The API will be available at `http://localhost:8080/docs`.

## Project Structure

```
.
├── .devcontainer/      # VS Code Dev Container configuration
├── config/             # Environment variable files (.env)
├── docs/               # Detailed documentation
├── src/                # Application source code
│   ├── api/            # API layer (FastAPI endpoints)
│   ├── backend/        # Service layer (business logic)
│   └── database/       # Database layer (repository, models)
└── tests/              # Pytest tests
```

## Documentation

For more detailed information, please refer to the guides in the `docs/` directory:

-   [**01-installation.md**](./docs/01-installation.md): Full setup instructions.
-   [**02-configuration.md**](./docs/02-configuration.md): How to manage environment variables.
-   [**03-architecture.md**](./docs/03-architecture.md): A deep dive into the code structure.
-   [**04-testing.md**](./docs/04-testing.md): How to run and write tests.
-   [**05-conventions.md**](./docs/05-conventions.md): Coding standards and practices.

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](./CONTRIBUTING.md) to get started.

