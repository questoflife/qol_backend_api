"""
Shared pytest fixtures for the Quest of Life Backend API tests.
"""
import pytest
import os
from fastapi import Request

from src.database.models import Base
from tests.database_utils import (
    create_pytest_engine_and_session_factory,
    _ensure_test_environment,
    create_test_schema_once,
    drop_test_schema,
)
from src.database.config import get_app_async_session
from src.api.deps import get_current_discord_id
from src.app import app

# Ensure tests are only run in the test environment
_ensure_test_environment()

@pytest.fixture(scope="session")
async def test_db_session_scope():
    """Session-scoped async fixture: ensure schema exists, drop at end."""
    await create_test_schema_once()
    yield
    await drop_test_schema()

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
async def clean_db(test_db_session_scope, session_factory):
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
    Sets up FastAPI dependency overrides for testing:
    1. Uses a clean test DB session per request
    2. Mocks authentication to return a test user (bypasses OAuth)
    Yields:
        None
    """
    async def _override_session():
        async with session_factory() as session:
            yield session
    
    async def _override_auth(request: Request):
        # Mock authentication - return a test Discord ID
        # This bypasses the OAuth flow for testing
        return "test_user_123"
    
    app.dependency_overrides[get_app_async_session] = _override_session
    app.dependency_overrides[get_current_discord_id] = _override_auth
    yield
    app.dependency_overrides.clear()
