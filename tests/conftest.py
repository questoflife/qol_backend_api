"""
Shared pytest fixtures for the Quest of Life Backend API tests.
"""
import pytest
import os

from app.database.models import Base
from tests.database_utils import destructive_recreate_database_and_tables, destructive_drop_test_database, get_pytest_session_factory

# Ensure tests are only run in the test environment
if os.getenv("APP_ENV") != "test":
    raise RuntimeError("Tests must be run with APP_ENV=test! Set APP_ENV in your .env.test file.")

@pytest.fixture(scope="session")
async def test_database():
    """
    Session-scoped fixture that sets up and tears down the pytest database.
    Runs once per test session.
    """
    # Setup
    await destructive_recreate_database_and_tables()
    
    yield  # This is where tests run
    
    # Teardown
    await destructive_drop_test_database()


@pytest.fixture
async def clean_db(test_database):
    """
    Function-scoped fixture that provides a clean database session.
    Clears all data before and after each test.
    """
    # Create session
    session_factory = get_pytest_session_factory()
    async with session_factory() as session:
        # Clear all data BEFORE test (clean start)
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        yield session
        # Clear all data AFTER test (clean for next test)
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        # Session is automatically closed by the context manager 