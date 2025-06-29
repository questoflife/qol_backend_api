"""
Shared pytest fixtures for the Quest of Life Backend API tests.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.config import get_engine, get_session_factory
from app.database.models import Base
from tests.database_utils import create_fresh_database, create_tables, teardown_database


@pytest.fixture(scope="session")
async def test_database():
    """
    Session-scoped fixture that sets up and tears down the test database.
    Runs once per test session.
    """
    # Setup
    await create_fresh_database()
    await create_tables()
    
    yield  # This is where tests run
    
    # Teardown
    await teardown_database()


@pytest.fixture
async def clean_db(test_database):
    """
    Function-scoped fixture that provides a clean database session.
    Clears all data before and after each test.
    """
    # Create session
    session_factory = get_session_factory()
    async with session_factory() as session:
        # Clear all data BEFORE test (clean start)
        engine = get_engine()
        async with engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(table.delete())
        
        yield session
        
        # Clear all data AFTER test (clean for next test)
        async with engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(table.delete())
        
        # Session is automatically closed by the context manager 