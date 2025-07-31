# syntax=docker/dockerfile:1

#################################################################
## Global build arguments
#################################################################
ARG APP_VERSION=0.1.0
ARG APP_NAME="QoL Backend API"
ARG APP_VENDOR="Quest of Life"

#################################################################
## BASE BUILDER - Sets up Python and Poetry dependency management
#################################################################
FROM python:3.12-slim as base-builder

# Set Poetry environment variables
ENV POETRY_VERSION=2.1.3 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_VIRTUALENVS_IN_PROJECT=true

# Install Poetry and build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gcc \
        libffi-dev && \
    # Install Poetry (uses POETRY_VERSION and POETRY_HOME)
    curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry && \
    # Clean up to reduce image size
    apt-get purge -y curl && \
    apt-get auto-remove -y && \
    rm -rf /var/lib/apt/lists/*

# Set workdir to /venv so Poetry creates the virtual environment at /venv/.venv
# This keeps the venv separate from /qol_backend_api (which gets bind-mounted in dev)
# and makes it easy to copy the venv to runtime stages at the same predictable path
WORKDIR /venv
COPY pyproject.toml poetry.lock ./

#################################################################
## RUNTIME BASE - Shared by all targets
#################################################################
FROM python:3.12-slim as runtime-base

ENV PATH="/venv/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=1 \
    PYTHONPATH=/qol_backend_api

WORKDIR /qol_backend_api

# Expose the default port for the API
EXPOSE 8000

# Add non-root user for security
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser && \
    mkdir -p /venv && \
    chown appuser:appuser /venv

# Note: We switch to non-root user in each target stage before running commands


#################################################################
## PRODUCTION - Minimal image for running the API
#################################################################
FROM base-builder AS prod-builder
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root --only main

# ---------------------------------------------------------------
FROM runtime-base AS prod

# Copy virtual environment from builder stage
COPY --from=prod-builder --link /venv/.venv /venv/.venv

# Copy only the application source code
COPY src ./src

# Add metadata labels
LABEL org.opencontainers.image.title="${APP_NAME}" \
      org.opencontainers.image.description="${APP_NAME}" \
      org.opencontainers.image.vendor="${APP_VENDOR}" \
      org.opencontainers.image.version="${APP_VERSION}"

# Switch to non-root user for security
USER appuser

# Start the API server
ENTRYPOINT ["python", "-m", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]

#################################################################
## TESTING - Environment for running tests
#################################################################
FROM prod-builder AS testing-builder
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root --with testing

# ---------------------------------------------------------------
FROM runtime-base AS testing

# Override PYTHONOPTIMIZE for testing - we need assertions to work properly
ENV PYTHONOPTIMIZE=0

# Copy virtual environment from builder stage
COPY --from=testing-builder --link /venv/.venv /venv/.venv

# Copy application code and test files
COPY src ./src/
COPY tests ./tests/
COPY pytest.ini ./

# Copy startup script with execute permission
COPY --chmod=0755 startup_with_testing.sh /usr/local/bin/

# Fix file ownership for pytest cache creation (must be done as root)
USER root
RUN chown -R appuser:appuser /qol_backend_api

# Switch to non-root user for security
USER appuser

# Add metadata labels
LABEL org.opencontainers.image.title="${APP_NAME} - Testing" \
      org.opencontainers.image.description="${APP_NAME} - Testing Environment" \
      org.opencontainers.image.vendor="${APP_VENDOR}" \
      org.opencontainers.image.version="${APP_VERSION}"

# Start the testing environment
CMD ["/usr/local/bin/startup_with_testing.sh"]