# syntax=docker/dockerfile:1

# Allow dynamic selection of the Python base image
ARG PYTHON_IMAGE=python:3.12-slim
FROM ${PYTHON_IMAGE}

# ---- Poetry (isolated, pinned) ----
ARG POETRY_VERSION=2.1.3
ENV POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && curl -sSL https://install.python-poetry.org | python3 - --version "$POETRY_VERSION" \
    && ln -s $POETRY_HOME/bin/poetry /usr/local/bin/poetry \
    && apt-get purge -y curl && rm -rf /var/lib/apt/lists/*


# ---- Dependencies ----
WORKDIR /app

COPY pyproject.toml poetry.lock ./

ARG PACKAGES=prod  # prod, testing, dev

RUN if [ "$PACKAGES" = "dev" ]; then \
      poetry install --no-root --with testing,dev; \
    elif [ "$PACKAGES" = "test" ]; then \
      poetry install --no-root --with testing; \
    else \
      poetry install --no-root --only main; \
    fi

# ---- Application ----

COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]