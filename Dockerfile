# syntax=docker/dockerfile:1.6

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
    useradd -u 1000 -g appuser -s /bin/sh -m appuser && \
    mkdir -p /venv && \
    chown appuser:appuser /venv
# Note: We switch to non-root user right before running ENTRYPOINT or CMD


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

# Switch to non-root user for security
USER appuser

# Add metadata labels
LABEL org.opencontainers.image.title="${APP_NAME}" \
      org.opencontainers.image.description="${APP_NAME}" \
      org.opencontainers.image.vendor="${APP_VENDOR}" \
      org.opencontainers.image.version="${APP_VERSION}"

ENTRYPOINT ["python", "-m", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]

#################################################################
## TESTING - Environment for running tests
#################################################################
FROM prod-builder AS testing-builder
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root --with testing


# ---------------------------------------------------------------
FROM runtime-base AS testing
# Copy virtual environment from builder stage
COPY --from=testing-builder --link /venv/.venv /venv/.venv
# Copy application code and test files
COPY src ./src/
COPY tests ./tests/
COPY pytest.ini ./

# Copy startup script with execute permission
COPY --chmod=0755 startup_with_testing.sh /usr/local/bin/

# Add metadata labels
LABEL org.opencontainers.image.title="${APP_NAME} - Testing" \
      org.opencontainers.image.description="${APP_NAME} - Testing Environment" \
      org.opencontainers.image.vendor="${APP_VENDOR}" \
      org.opencontainers.image.version="${APP_VERSION}"

# Switch to non-root user for security
USER appuser

CMD ["/usr/local/bin/startup_with_testing.sh"]

#################################################################
## DEVELOPMENT - Customizable environment for local development
#################################################################
FROM testing-builder AS dev-builder

# Install custom build dependencies from config/apt-build-packages.txt
COPY config/apt-build-packages.txt* /tmp/
RUN if [ -f /tmp/apt-build-packages.txt ]; then \
        echo "Installing build dependencies from config/apt-build-packages.txt..."; \
        apt-get update && \
        apt-get install -y --no-install-recommends $(grep -v "^#" /tmp/apt-build-packages.txt | tr '\n' ' ') && \
        rm -rf /var/lib/apt/lists/*; \
    else \
        echo "No config/apt-build-packages.txt file found."; \
    fi

# Install custom Python packages from config/python-dev-packages.txt
COPY config/python-dev-packages.txt* /tmp/
RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    if [ -f /tmp/python-dev-packages.txt ]; then \
        # Create dev group if it doesn't exist yet
        poetry group add dev || true; \
        \
        # Process and install packages
        grep -v "^#" /tmp/python-dev-packages.txt | grep -v "^$" > /tmp/filtered-packages.txt; \
        if [ -s /tmp/filtered-packages.txt ]; then \
            echo "Installing Python development packages from config/python-dev-packages.txt..."; \
            # Install packages one at a time, continuing if some fail
            cat /tmp/filtered-packages.txt | xargs -r -L 1 poetry add --group=dev || true; \
        else \
            echo "No packages found in config/python-dev-packages.txt (empty or only comments)."; \
        fi; \
        rm /tmp/filtered-packages.txt; \
    else \
        echo "No config/python-dev-packages.txt found. Create one from config/python-dev-packages.txt.example for custom packages."; \
    fi


# ---------------------------------------------------------------
FROM runtime-base AS dev

# Install interactive development tools from config/apt-runtime-packages.txt
COPY config/apt-runtime-packages.txt* /tmp/
RUN if [ -f /tmp/apt-runtime-packages.txt ]; then \
        echo "Installing runtime packages from config/apt-runtime-packages.txt..."; \
        apt-get update && \
        apt-get install -y --no-install-recommends $(grep -v "^#" /tmp/apt-runtime-packages.txt | tr '\n' ' ') && \
        rm -rf /var/lib/apt/lists/*; \
    else \
        echo "No config/apt-runtime-packages.txt found. Create one from config/apt-runtime-packages.txt.example for custom tools."; \
    fi

# Copy the Python virtual environment with all dependencies
COPY --from=dev-builder --link /venv/.venv /venv/.venv

# Set the working directory
WORKDIR /qol_backend_api

# Note: Project files will be mounted from host via volume bind mount
# instead of being copied into the container

# Add metadata labels
LABEL org.opencontainers.image.title="${APP_NAME} - Development" \
      org.opencontainers.image.description="${APP_NAME} - Development Environment" \
      org.opencontainers.image.vendor="${APP_VENDOR}" \
      org.opencontainers.image.version="${APP_VERSION}"

# Switch to non-root user for security
USER appuser

# Keep container running for development
CMD ["sleep", "infinity"]