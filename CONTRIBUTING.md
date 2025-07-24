# Contributing Guidelines

We welcome contributions from the community. To ensure a smooth process, please follow these guidelines.

## Getting Started

1.  Fork the repository.
2.  Clone your fork locally.
3.  Follow the [Installation Guide](./docs/01-installation.md) to set up your development environment. The recommended method is using the VS Code Dev Container.

## Making Changes

1.  Create a new branch for your changes:
    ```bash
    git checkout -b feature/your-feature-name
    ```
2.  Make your code changes.
3.  Ensure your code adheres to the project's [Conventions](./docs/05-conventions.md).
4.  Run tests to ensure you haven't introduced any regressions:
    ```bash
    docker compose --profile testing up
    ```
5.  Commit your changes with a clear and descriptive commit message.

## Submitting a Pull Request

1.  Push your branch to your fork:
    ```bash
    git push origin feature/your-feature-name
    ```
2.  Open a Pull Request (PR) from your fork to the `main` branch of the original repository.
3.  Provide a clear title and description for your PR, explaining the changes you've made.
4.  Your PR will be reviewed, and we may request changes. Please be responsive to feedback.

Thank you for contributing!
