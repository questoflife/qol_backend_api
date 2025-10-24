"""Test database utilities.

Focus on safe, test-only helpers for creating async engines, sessions, and
managing schema lifecycle. All helpers enforce that the configured DB name
contains 'test' to reduce risk of accidental destructive operations against
non-test databases.
"""
from src.settings import get_settings
from src.database.config import create_app_async_engine, create_app_async_session_factory
from src.database.models import BaseModel


def _ensure_test_environment():
    """
    Ensures that the environment is safe for destructive test operations.
    Checks that DB_NAME contains 'test'.
    Raises RuntimeError if not safe.
    """
    if "test" not in get_settings().DB_NAME.lower():
        raise RuntimeError(f"Operation can only be run if DB_NAME contains 'test' (got DB_NAME={get_settings().DB_NAME})!")

def create_pytest_engine_and_session_factory():
    """
    Always use this function for engine and session factory creation in tests!
    Ensures tests only run in the test environment.
    Returns:
        (engine, session_factory):
            - engine: a fresh async SQLAlchemy engine (must be disposed by the caller)
            - session_factory: a fresh async session factory bound to the engine
    Usage:
        engine, session_factory = create_pytest_engine_and_session_factory()
        async with session_factory() as session:
            ...
        await engine.dispose()
    """
    _ensure_test_environment()
    engine = create_app_async_engine()
    session_factory = create_app_async_session_factory(engine)
    return engine, session_factory 


async def create_test_schema_once():
    """Create all tables (idempotent) using a fresh test engine.

    Uses create_pytest_engine_and_session_factory to ensure consistency with
    other test session usage and to avoid shared global state that might leak
    across tests.
    """
    _ensure_test_environment()
    engine, _session_factory = create_pytest_engine_and_session_factory()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)
    finally:
        await engine.dispose()


async def drop_test_schema():
    """Drop all tables using a fresh engine (best-effort at teardown)."""
    _ensure_test_environment()
    engine, _session_factory = create_pytest_engine_and_session_factory()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.drop_all)
    finally:
        await engine.dispose()