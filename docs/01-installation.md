# Installation Guide

This guide provides instructions for setting up the project for development. The recommended approach is using Docker and the VS Code Dev Container, which provides a consistent and reproducible environment.

## Recommended: Docker & VS Code Dev Container

This is the easiest and most reliable way to get started. It ensures that you have the exact same development environment as the rest of the team and CI/CD pipelines.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [VS Code Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Steps

1.  **Clone the repository.**
2.  **Open the project in VS Code.**
3.  When prompted, click **"Reopen in Container"**. VS Code will automatically build the Docker image defined in `Dockerfile` and configure your development environment.

### Running the Application

The project uses `docker-compose.yml` to manage services. We use profiles to run different configurations.

-   **Development (`dev-db`):** Runs the FastAPI application with hot-reloading and a dedicated development database.
    ```bash
    docker compose --profile dev-db up --build
    ```
    The API will be available at `http://localhost:8080`.

-   **Testing (`testing`):** Runs the test suite against a dedicated, ephemeral test database.
    ```bash
    docker compose --profile testing up --build
    ```

-   **Production (`prod`):** Simulates the production environment.
    ```bash
    docker compose --profile prod up --build
    ```

## Alternative: Local Setup (Manual)

If you prefer not to use Docker, you can set up the project locally.

### Prerequisites

1.  **Python 3.12**
2.  **Poetry** (Dependency Manager)
3.  **MySQL 8+** (Database Server)

### Steps

1.  **Install Dependencies:**
    ```bash
    poetry install
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file in the root directory and configure it to point to your local MySQL instance. See `docs/02-configuration.md` for details.

3.  **Run the Application:**
    ```bash
    python -m src.app
    ```
