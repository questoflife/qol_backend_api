"""
Database setup for the Quest of Life Backend API.
Configures the async SQLAlchemy engine and session factory.

ENVIRONMENT ARCHITECTURE:
This module is environment-agnostic. It reads all configuration from environment variables.
- DB_NAME/DATABASE_URL: Used for all application logic, including tests, dev, and prod.
- The environment (e.g., APP_ENV) should be set externally in .env to control which database is used.
- All test and destructive logic is handled in test utilities, not here.

This ensures the config is simple, robust, and safe for all environments.
"""
import os
from typing import AsyncGenerator
from functools import lru_cache
import sys

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


# --- Load environment variables from .env file ---
load_dotenv()


# Global variable declarations (type only, no assignment)
ASYNC_SERVER_URL: str
SYNC_SERVER_URL: str
DB_NAME: str
_engine = None
_async_session_factory = None


# Configuration/init functions
def _init_config():
    """Initialize configuration constants."""
    global ASYNC_SERVER_URL, SYNC_SERVER_URL, DB_NAME
    # Get database configuration
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    if not all([db_user, db_password, db_host, db_port, db_name]):
        raise RuntimeError(
            "Database configuration is incomplete. "
            "Set all of DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, and DB_NAME.")
    ASYNC_SERVER_URL = f"mysql+aiomysql://{db_user}:{db_password}@{db_host}:{db_port}"
    SYNC_SERVER_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}"
    DB_NAME = db_name  # type: ignore


# Call to initialize config
_init_config()


# --- Pure creation functions ---
def create_app_async_engine():
    """
    Create a new async SQLAlchemy engine for the app's configured database (from .env).
    """
    return create_async_engine(f"{ASYNC_SERVER_URL}/{DB_NAME}", echo=True)


def create_app_async_session_factory(engine):
    """
    Create a new async session factory for the app's configured database (from .env) using the provided engine.
    """
    return async_sessionmaker(engine, expire_on_commit=False)


# --- Cached manager functions for production ---
@lru_cache(maxsize=1)
def get_cached_app_async_engine():
    """Get the cached async engine for the app's configured database (from .env)."""
    return create_app_async_engine()


@lru_cache(maxsize=1)
def get_cached_app_async_session_factory():
    """Get the cached async session factory for the app's configured database (from .env)."""
    engine = get_cached_app_async_engine()
    return create_app_async_session_factory(engine)


# --- Dependency for FastAPI ---
async def get_app_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an async SQLAlchemy session using the cached session factory.
    Yields:
        AsyncSession: An active SQLAlchemy async session.
    """
    session_factory = get_cached_app_async_session_factory()
    async with session_factory() as session:
        yield session
