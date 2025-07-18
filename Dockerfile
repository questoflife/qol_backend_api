# syntax=docker/dockerfile:1.6

# ---- BASE + POETRY (shared by every target) ----
FROM python:3.12-slim as base-builder
ARG POETRY_VERSION=2.1.3

ENV POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    VIRTUAL_ENV=/app/.venv

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -sSL https://install.python-poetry.org | python3 - --version "${POETRY_VERSION}" && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry && \
    apt-get purge -y curl && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

# ---- RUNTIME-BASE RUNTIME (shared by every target) ----
FROM python:3.12-slim as runtime-base
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
WORKDIR /app


# ---- PROD ----
FROM base-builder AS prod-builder
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root --only main

FROM runtime-base AS prod
COPY --from=prod-builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY src ./src
ENTRYPOINT ["python", "-m", "app.main"]

# ---- TESTING ----
FROM prod-builder AS testing-builder
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root --with testing

FROM runtime-base AS testing
COPY --from=testing-builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY src tests pytest.ini ./

ENTRYPOINT ["pytest"]

# ---- DEV ----
FROM testing-builder AS dev-builder
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root --with testing,dev

FROM runtime-base AS dev
COPY --from=dev-builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY . .

ENTRYPOINT ["bash"]