"""
Shared pytest fixtures for the Quest of Life Backend API tests.
"""
import pytest
import os

from app.database.models import Base
from tests.database_utils import destructive_recreate_database_and_tables, destructive_drop_test_database, create_pytest_engine_and_session_factory, _ensure_test_environment
from app.database.config import get_app_async_session
from app.main import app

# Ensure tests are only run in the test environment
_ensure_test_environment()

@pytest.fixture(scope="session")
def test_database():
    """
    Session-scoped fixture that sets up and tears down the pytest database.
    Runs once per test session.
    """
    # Setup
    destructive_recreate_database_and_tables()
    yield  # This is where tests run
    # Teardown
    destructive_drop_test_database()

@pytest.fixture
async def session_factory():
    """
    Provides a fresh async session factory for use in tests.
    Yields:
        session_factory: async session factory bound to a test engine.
    """
    engine, session_factory = create_pytest_engine_and_session_factory()
    yield session_factory
    await engine.dispose()

@pytest.fixture
async def clean_db(test_database, session_factory):
    """
    Cleans all tables before and after each test.
    Ensures a clean database state for every test function.
    """
    # Clean all tables before test
    async with session_factory() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()
    yield
    # Clean all tables after test
    async with session_factory() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()

@pytest.fixture
async def clean_db_session(clean_db, session_factory):
    """
    Provides a clean database session for direct DB access in tests.
    Depends on clean_db to ensure the DB is cleaned before and after.
    Yields:
        session: async database session.
    """
    async with session_factory() as session:
        yield session

@pytest.fixture
async def clean_db_override_app_session(clean_db, session_factory):
    """
    Sets up FastAPI dependency override to use a clean DB session per request during tests.
    Yields:
        None
    """
    async def _override():
        async with session_factory() as session:
            yield session
    app.dependency_overrides[get_app_async_session] = _override
    yield
    app.dependency_overrides.clear() 