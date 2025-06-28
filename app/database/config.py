"""
Database setup for the Quest of Life Backend API.
Configures the async SQLAlchemy engine and session factory.
"""
import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


# --- Load environment variables from .env file (for local development) ---
load_dotenv()

# Try to get DATABASE_URL directly, otherwise construct it from individual fields
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    if not all([db_user, db_password, db_host, db_port, db_name]):
        raise RuntimeError(
            "Database configuration is incomplete. "
            "Set either DATABASE_URL or all of DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, and DB_NAME.")
    # SQLAlchemy async MySQL URL format
    DATABASE_URL = f"mysql+aiomysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Create the async SQLAlchemy engine (internal use only)
_engine = create_async_engine(DATABASE_URL, echo=True)
# Create the async session factory (internal use only)
_async_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an async SQLAlchemy session.
    Yields:
        AsyncSession: An active SQLAlchemy async session.
    """
    async with _async_session_factory() as session:
        yield session 