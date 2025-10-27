"""
Async SQLAlchemy database configuration for Quest of Life Backend API.

- Reads all settings from environment variables.
- Environment-agnostic: does not enforce test/dev/prod safety; all safety is handled in test utilities and entry points (see README).
- In development: use docker-compose env_file or local .env
- In production: use secret injection (K8s secrets, Docker secrets, etc.)
"""
import os
import ssl
from typing import AsyncGenerator
from functools import lru_cache
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine

from src.settings import get_settings

# Global variable declarations (type only, no assignment)
_engine = None
_async_session_factory = None


def create_app_async_engine() -> AsyncEngine:
    """Create a new async SQLAlchemy engine for the configured database."""
    url = f"{get_settings().ASYNC_SERVER_URL}/{get_settings().DB_NAME}"
    # TLS enforcement: always attempt an encrypted connection.
    # Optional verification disable (for local dev/test with self-signed MySQL auto certs):
    #   Set DB_SSL_DISABLE_VERIFICATION=true to skip hostname & cert validation.
    #   WARNING: Never set this in production; it weakens security (MITM risk).
    ssl_ctx = ssl.create_default_context()
    disable_verification = get_settings().DB_SSL_DISABLE_VERIFICATION
    if disable_verification:
        print("WARNING: SSL verification is DISABLED for the database connection.")
        # Relax verification while still encrypting the transport.
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE  # type: ignore[attr-defined]
    connect_args = {"ssl": ssl_ctx}
    return create_async_engine(url, echo=True, connect_args=connect_args)


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


async def create_test_tables_if_not_exist():
    """
    Create all database tables if they don't already exist.
    
    SAFETY: Only runs if DB_NAME contains 'test'.
    
    This is idempotent - it will only create tables that don't exist.
    
    Raises:
        RuntimeError: If DB_NAME does not contain 'test'
    """
    from src.database.models import BaseModel
    from tests.database_utils import _ensure_test_environment
    
    _ensure_test_environment()
    
    engine = get_cached_app_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
