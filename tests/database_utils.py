"""
Database utilities for testing.
Provides functions to create and manage test databases.

SAFETY PRINCIPLE:
These utilities ONLY use DB_NAME_TEST (never DB_NAME) to guarantee they can never
accidentally operate on production databases. This is a critical safety measure.

- DB_NAME_TEST is only available when running pytest
- If DB_NAME_TEST is None, these functions fail with clear error messages
- This prevents any possibility of accidentally dropping/creating production databases

Even though DB_NAME points to the test database when running pytest, we use DB_NAME_TEST
as an explicit safety guarantee that we're working with test data.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.database.config import get_engine, get_session_factory, DB_NAME_TEST, SERVER_URL


async def create_fresh_database() -> None:
    """
    Create a fresh test database by dropping and recreating it.
    This ensures a clean state for each test run.
    """
    if DB_NAME_TEST is None:
        raise RuntimeError("Test database not available - not running in pytest mode")
    
    # Create a connection without specifying a database
    temp_engine = create_async_engine(SERVER_URL, echo=False)
    
    async with temp_engine.begin() as conn:
        # Drop database if it exists
        await conn.execute(text(f"DROP DATABASE IF EXISTS `{DB_NAME_TEST}`"))
        # Create fresh database
        await conn.execute(text(f"CREATE DATABASE `{DB_NAME_TEST}`"))
    
    await temp_engine.dispose()


async def create_tables() -> None:
    """
    Create all tables in the database.
    This should be called after create_fresh_database().
    """
    from app.database.models import Base
    
    if DB_NAME_TEST is None:
        raise RuntimeError("Test database not available - not running in pytest mode")
    
    engine = get_engine()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def teardown_database() -> None:
    """
    Clean up the test database.
    This is optional but good practice for cleanup.
    """
    if DB_NAME_TEST is None:
        raise RuntimeError("Test database not available - not running in pytest mode")
    
    engine = get_engine()
    await engine.dispose()


async def get_test_session():
    """
    Get a test database session.
    This is a convenience function for tests that need a session.
    """
    if DB_NAME_TEST is None:
        raise RuntimeError("Test database not available - not running in pytest mode")
    
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session 