# Conventions Guide

This document outlines the coding styles, tools, and practices used in this project to ensure consistency and quality.

## Code Formatting & Linting

We use a combination of tools to maintain a consistent code style. These are automatically run by the testing pipeline.

-   **Black:** For uncompromising code formatting.
-   **Ruff:** For linting and style checks.

You can run these tools locally before committing your code:
```bash
poetry run black .
poetry run ruff .
```

## Editor Configuration (`.editorconfig`)

The `.editorconfig` file in the root of the project helps maintain consistent coding styles between different editors and IDEs. It automatically configures settings like:
-   Indent style: `space`
-   Indent size: `4`
-   End of line: `lf` (Unix-style line endings)
-   Charset: `utf-8`

Most modern editors will automatically detect and apply these settings.

## Git Attributes (`.gitattributes`)

The `.gitattributes` file ensures consistent line endings across all operating systems. It is configured to enforce `LF` (Unix-style) line endings for all text files. This is crucial for preventing issues in shell scripts and Docker builds.

```
* text=auto eol=lf
```

This tells Git to automatically convert `CRLF` line endings to `LF` on commit.

## Git Workflow

We follow a simple feature-branch workflow:
1.  Create a new branch from `main` for your feature or bugfix (e.g., `feature/add-new-endpoint` or `fix/user-auth-bug`).
2.  Make your changes and commit them.
3.  Push your branch to the remote repository.
4.  Open a Pull Request (PR) against the `main` branch.
5.  The PR will be reviewed, and once approved, it will be merged.
