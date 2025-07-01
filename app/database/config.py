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
import sys

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


# --- Load environment variables from .env file ---
load_dotenv()


# Global variable declarations (type only, no assignment)
SERVER_URL: str
DB_NAME: str
DATABASE_URL: str
_engine = None
_async_session_factory = None


# Configuration/init functions
def _init_config():
    """Initialize configuration constants."""
    global SERVER_URL, DB_NAME, DATABASE_URL
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
    SERVER_URL = f"mysql+aiomysql://{db_user}:{db_password}@{db_host}:{db_port}"
    DB_NAME = db_name  # type: ignore
    DATABASE_URL = f"{SERVER_URL}/{DB_NAME}"


# Call to initialize config
_init_config()


def get_engine():
    """Get or create the async SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(DATABASE_URL, echo=True)
    return _engine


def get_session_factory():
    """Get or create the async session factory."""
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _async_session_factory


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an async SQLAlchemy session.
    Yields:
        AsyncSession: An active SQLAlchemy async session.
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session 