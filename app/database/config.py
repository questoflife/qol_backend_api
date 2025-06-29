"""
Database setup for the Quest of Life Backend API.
Configures the async SQLAlchemy engine and session factory.

SAFETY ARCHITECTURE:
This module implements a dual-database safety system to prevent accidental
modification of production data during testing:

1. DB_NAME/DATABASE_URL: Used by main application logic
2. DB_NAME_TEST/DATABASE_URL_TEST: Used by test utilities (safety guarantee)

When running pytest:
- DB_NAME points to test database (for application logic)
- DB_NAME_TEST points to same test database (for test utilities)
- Test utilities ONLY use DB_NAME_TEST to guarantee they never touch production

When not running pytest:
- DB_NAME points to production database
- DB_NAME_TEST is None (test utilities fail with clear error)

This ensures test utilities can never accidentally operate on production data,
even if there are bugs in the pytest detection logic.
"""
import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


# --- Load environment variables from .env file ---
load_dotenv()


# Global configuration constants
SERVER_URL: str
DB_NAME: str
DATABASE_URL: str
DB_NAME_TEST: str | None
DATABASE_URL_TEST: str | None


def _validate_test_database(db_name: str) -> None:
    """
    Validate that test database names are safe to use.
    
    Args:
        db_name: The database name to validate
        
    Raises:
        RuntimeError: If the database name doesn't indicate it's a test database
    """
    if not db_name.lower().endswith('_test') and not db_name.lower().startswith('test'):
        raise RuntimeError(
            f"Safety check failed: Database '{db_name}' doesn't appear to be a test database. "
            "Test databases must end with '_test' or start with 'test' to prevent "
            "accidentally modifying production data."
        )


def _init_config():
    """Initialize configuration constants."""
    global SERVER_URL, DB_NAME, DATABASE_URL, DB_NAME_TEST, DATABASE_URL_TEST
    
    # Get database configuration
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    
    if not all([db_user, db_password, db_host, db_port]):
        raise RuntimeError(
            "Database configuration is incomplete. "
            "Set all of DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, and DB_NAME.")
    
    # Construct server URL (shared between main and test)
    SERVER_URL = f"mysql+aiomysql://{db_user}:{db_password}@{db_host}:{db_port}"
    
    # Check if we're running pytest (automatic detection)
    if "pytest" in os.environ.get("PYTEST_CURRENT_TEST", ""):
        # In testing mode, use test database for both main and test variables
        db_name_test = os.getenv("DB_NAME_TEST")
        if not db_name_test:
            raise RuntimeError("DB_NAME_TEST is not set")
        # Validate test database name for safety
        _validate_test_database(db_name_test)
        
        # Set both main and test variables to test database
        DB_NAME = db_name_test
        DATABASE_URL = f"{SERVER_URL}/{DB_NAME}"

        DB_NAME_TEST = DB_NAME
        DATABASE_URL_TEST = DATABASE_URL
    else:
        # In production mode, use main database
        db_name = os.getenv("DB_NAME")
        if not db_name:
            raise RuntimeError("DB_NAME is not set")
        
        DB_NAME = db_name
        DATABASE_URL = f"{SERVER_URL}/{DB_NAME}"
        # Set test variables to None when not in testing mode
        DB_NAME_TEST = None
        DATABASE_URL_TEST = None


# Initialize configuration constants
_init_config()

# Lazy engine and session factory creation
_engine = None
_async_session_factory = None


def get_engine():
    """Get or create the async SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(DATABASE_URL, echo=True)
    return _engine


def get_session_factory():
    """Get or create the async session factory."""
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _async_session_factory


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an async SQLAlchemy session.
    Yields:
        AsyncSession: An active SQLAlchemy async session.
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session 