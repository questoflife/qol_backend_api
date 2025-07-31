"""
Database functionality tests for the Quest of Life Backend API.
Tests the repository layer and database operations.
"""
import pytest
from sqlalchemy.future import select

from src.database.models import UserKeyValue
from src.database.repository import get_user_key_value, set_user_key_value


# ============================================================================
# FIXTURES FOR KEY-VALUE FUNCTIONALITY TESTS
# ============================================================================

@pytest.fixture
async def user1(clean_db_session):
    """Create user1 with a single key-value pair."""
    await set_user_key_value(clean_db_session, "user1", "theme", "light")


@pytest.fixture
async def user1_updated(user1, clean_db_session):
    """Create user1 with an updated key-value pair."""
    await set_user_key_value(clean_db_session, "user1", "theme", "dark")


@pytest.fixture
async def user1_multiple_keys(user1, clean_db_session):
    """Create user1 with multiple key-value pairs."""
    await set_user_key_value(clean_db_session, "user1", "language", "en")


@pytest.fixture
async def user2(clean_db_session):
    """Create user2 with the same key as user1."""
    await set_user_key_value(clean_db_session, "user2", "theme", "light")


# ============================================================================
# KEY-VALUE CRUD OPERATIONS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_key_value(user1, clean_db_session):
    """Test creating a user key-value pair."""
    value = await get_user_key_value(clean_db_session, "user1", "theme")
    assert value == "light"


@pytest.mark.asyncio
async def test_update_key_value(user1_updated, clean_db_session):
    """Test updating an existing key-value pair."""
    value = await get_user_key_value(clean_db_session, "user1", "theme")
    assert value == "dark"


@pytest.mark.asyncio
async def test_add_second_key(user1_multiple_keys, clean_db_session):
    """Test adding a second key to an existing user."""
    value = await get_user_key_value(clean_db_session, "user1", "language")
    assert value == "en"
    
    # Verify the original theme key remains unchanged
    theme_value = await get_user_key_value(clean_db_session, "user1", "theme")
    assert theme_value == "light"


@pytest.mark.asyncio
async def test_create_user2(user2, clean_db_session):
    """Test creating a second user with the same key."""
    value = await get_user_key_value(clean_db_session, "user2", "theme")
    assert value == "light"


# ============================================================================
# USER ISOLATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_user2_isolation(user1_updated, user2, clean_db_session):
    """Test that user2 creation doesn't interfere with user1."""
    # Verify user2 has theme=light
    user2_theme = await get_user_key_value(clean_db_session, "user2", "theme")
    assert user2_theme == "light"
    
    # Verify user1 still has theme=dark (from user1_updated)
    user1_theme = await get_user_key_value(clean_db_session, "user1", "theme")
    assert user1_theme == "dark"
    
    # Verify user2 has exactly one record
    result = await clean_db_session.execute(
        select(UserKeyValue).where(UserKeyValue.user_id == "user2")
    )
    user2_records = result.scalars().all()
    assert len(user2_records) == 1
    assert user2_records[0].key == "theme"
    assert user2_records[0].value == "light"
    
    # Verify user1 has exactly one record
    result = await clean_db_session.execute(
        select(UserKeyValue).where(UserKeyValue.user_id == "user1")
    )
    user1_records = result.scalars().all()
    assert len(user1_records) == 1
    assert user1_records[0].key == "theme"
    assert user1_records[0].value == "dark"


# ============================================================================
# EDGE CASES AND ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_get_nonexistent_user(clean_db_session):
    """Test getting a key for a user that doesn't exist."""
    value = await get_user_key_value(clean_db_session, "nonexistent_user", "theme")
    assert value is None


@pytest.mark.asyncio
async def test_get_nonexistent_key(user1, clean_db_session):
    """Test getting a key that doesn't exist for an existing user."""
    value = await get_user_key_value(clean_db_session, "user1", "nonexistent_key")
    assert value is None 