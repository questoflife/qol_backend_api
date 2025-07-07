"""
Async SQLAlchemy database configuration for Quest of Life Backend API.

- Reads all settings from environment variables (.env).
- Environment-agnostic: does not enforce test/dev/prod safety; all safety is handled in test utilities and entry points (see README).
"""
import os
from typing import AsyncGenerator
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine

# Load environment variables from .env file
load_dotenv()

# Global variable declarations (type only, no assignment)
ASYNC_SERVER_URL: str
SYNC_SERVER_URL: str
DB_NAME: str
_engine = None
_async_session_factory = None


def _init_config() -> None:
    """Initialize configuration constants from environment variables."""
    global ASYNC_SERVER_URL, SYNC_SERVER_URL, DB_NAME
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

# Initialize config on import
_init_config()


def create_app_async_engine() -> AsyncEngine:
    """Create a new async SQLAlchemy engine for the configured database."""
    return create_async_engine(f"{ASYNC_SERVER_URL}/{DB_NAME}", echo=True)


def create_app_async_session_factory(engine: AsyncEngine) -> async_sessionmaker:
    """Create a new async session factory for the configured database."""
    return async_sessionmaker(engine, expire_on_commit=False)


@lru_cache(maxsize=1)
def get_cached_app_async_engine() -> AsyncEngine:
    """Get a cached async engine for the configured database."""
    return create_app_async_engine()


@lru_cache(maxsize=1)
def get_cached_app_async_session_factory() -> async_sessionmaker:
    """Get a cached async session factory for the configured database."""
    engine = get_cached_app_async_engine()
    return create_app_async_session_factory(engine)


async def get_app_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency: yields an async SQLAlchemy session using the cached session factory.
    Yields:
        AsyncSession: An active SQLAlchemy async session.
    """
    session_factory = get_cached_app_async_session_factory()
    async with session_factory() as session:
        yield session
