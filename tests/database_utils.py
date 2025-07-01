"""
Destructive test database utilities for test environments only.
Provides functions to drop, recreate, and initialize the test database.

SAFETY PRINCIPLE:
- All functions require APP_ENV=test and will raise if not set.
- All destructive operations are clearly marked and should never be used outside of test environments.
- Always use create_pytest_engine_and_session_factory for session creation in tests. This ensures tests only run in the test environment and never touch production or dev databases.
- The caller is responsible for disposing the engine after use.
"""
from sqlalchemy import text, create_engine
import os
from app.database.config import DB_NAME, SYNC_SERVER_URL, create_app_async_engine, create_app_async_session_factory

def destructive_recreate_database_and_tables() -> None:
    """
    DANGEROUS: Drops and recreates the test database, then creates all tables.
    Only use in test environments! This is destructive and should never be used outside of APP_ENV=test.
    Only works if the database is completely empty after recreation.
    """
    if os.environ.get("APP_ENV") != "test":
        raise RuntimeError("destructive_recreate_database_and_tables can only be run with APP_ENV=test!")
    # Use server_engine for operations without a DB selected
    server_engine = create_engine(SYNC_SERVER_URL, echo=False)
    with server_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS `{DB_NAME}`"))
        conn.execute(text(f"CREATE DATABASE `{DB_NAME}`"))
    server_engine.dispose()
    # Use db_engine for operations with the DB selected
    from app.database.models import Base
    db_engine = create_engine(f"{SYNC_SERVER_URL}/{DB_NAME}", echo=False)
    with db_engine.begin() as conn:
        result = conn.execute(text("SHOW TABLES"))
        if result.first() is not None:
            raise RuntimeError("Database is not empty after recreation. Aborting table creation.")
        Base.metadata.create_all(conn)
    db_engine.dispose()

def destructive_drop_test_database() -> None:
    """
    DANGEROUS: Drops the test database itself. Only use in test environments!
    This is destructive and should never be used outside of APP_ENV=test.
    Disposes of the db_engine before dropping the database to avoid zombie connections.
    """
    if os.environ.get("APP_ENV") != "test":
        raise RuntimeError("destructive_drop_test_database can only be run with APP_ENV=test!")
    server_engine = create_engine(SYNC_SERVER_URL, echo=False)
    with server_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS `{DB_NAME}`"))
    server_engine.dispose()

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
    if os.getenv("APP_ENV") != "test":
        raise RuntimeError("create_pytest_engine_and_session_factory can only be used with APP_ENV=test!")
    engine = create_app_async_engine()
    session_factory = create_app_async_session_factory(engine)
    return engine, session_factory 