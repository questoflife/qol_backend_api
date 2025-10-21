"""
Database functionality tests for the Quest of Life Backend API.
Tests the repository layer and database operations.
"""
import pytest
from sqlalchemy.future import select

from src.database.models import UserValues
from src.database.commands import get_user_text, set_user_text
from src.database.private_commands import get_user_value, set_user_value
from src.database.errors import UserNotFoundError, ColumnNotFoundError


# ============================================================================
# FIXTURES FOR USER TEXT FUNCTIONALITY TESTS
# ============================================================================

@pytest.fixture
async def user1(clean_db_session):
    """Create user1 with initial text."""
    # First create the user row
    user = UserValues(user_id="user1", text=None)
    clean_db_session.add(user)
    await clean_db_session.commit()
    # Then set the text
    await set_user_text(clean_db_session, "user1", "Hello World")


@pytest.fixture
async def user1_updated(user1, clean_db_session):
    """Create user1 with updated text."""
    await set_user_text(clean_db_session, "user1", "Updated Text")


@pytest.fixture
async def user2(clean_db_session):
    """Create user2 with different text."""
    # First create the user row
    user = UserValues(user_id="user2", text=None)
    clean_db_session.add(user)
    await clean_db_session.commit()
    # Then set the text
    await set_user_text(clean_db_session, "user2", "User2 Text")


# ============================================================================
# USER TEXT CRUD OPERATIONS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_user_text(user1, clean_db_session):
    """Test creating a user with text."""
    value = await get_user_text(clean_db_session, "user1")
    assert value == "Hello World"


@pytest.mark.asyncio
async def test_update_user_text(user1_updated, clean_db_session):
    """Test updating an existing user's text."""
    value = await get_user_text(clean_db_session, "user1")
    assert value == "Updated Text"


@pytest.mark.asyncio
async def test_create_user2(user2, clean_db_session):
    """Test creating a second user with different text."""
    value = await get_user_text(clean_db_session, "user2")
    assert value == "User2 Text"


# ============================================================================
# USER ISOLATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_user2_isolation(user1_updated, user2, clean_db_session):
    """Test that user2 creation doesn't interfere with user1."""
    # Verify user2 has correct text
    user2_text = await get_user_text(clean_db_session, "user2")
    assert user2_text == "User2 Text"
    
    # Verify user1 still has updated text
    user1_text = await get_user_text(clean_db_session, "user1")
    assert user1_text == "Updated Text"
    
    # Verify user2 has exactly one record
    result = await clean_db_session.execute(
        select(UserValues).where(UserValues.user_id == "user2")
    )
    user2_records = result.scalars().all()
    assert len(user2_records) == 1
    assert user2_records[0].text == "User2 Text"
    
    # Verify user1 has exactly one record
    result = await clean_db_session.execute(
        select(UserValues).where(UserValues.user_id == "user1")
    )
    user1_records = result.scalars().all()
    assert len(user1_records) == 1
    assert user1_records[0].text == "Updated Text"


# ============================================================================
# EDGE CASES AND ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_get_nonexistent_user_raises_error(clean_db_session):
    """Test getting text for a user that doesn't exist raises UserNotFoundError."""
    with pytest.raises(UserNotFoundError):
        await get_user_value(clean_db_session, "nonexistent_user", "text")


@pytest.mark.asyncio
async def test_set_nonexistent_user_raises_error(clean_db_session):
    """Test setting text for a user that doesn't exist raises UserNotFoundError."""
    with pytest.raises(UserNotFoundError):
        await set_user_value(clean_db_session, "nonexistent_user", "text", "some value")


@pytest.mark.asyncio
async def test_get_nonexistent_column_raises_error(user1, clean_db_session):
    """Test getting a column that doesn't exist raises ColumnNotFoundError."""
    with pytest.raises(ColumnNotFoundError):
        await get_user_value(clean_db_session, "user1", "nonexistent_column")


@pytest.mark.asyncio
async def test_set_nonexistent_column_raises_error(user1, clean_db_session):
    """Test setting a column that doesn't exist raises ColumnNotFoundError."""
    with pytest.raises(ColumnNotFoundError):
        await set_user_value(clean_db_session, "user1", "nonexistent_column", "value")


@pytest.mark.asyncio
async def test_text_can_be_empty(clean_db_session):
    """Test that text can be set to empty string."""
    # Create user with empty text
    user = UserValues(user_id="user_empty", text="")
    clean_db_session.add(user)
    await clean_db_session.commit()
    
    value = await get_user_text(clean_db_session, "user_empty")
    assert value == ""


@pytest.mark.asyncio
async def test_text_can_be_null(clean_db_session):
    """Test that text can be null."""
    # Create user with null text
    user = UserValues(user_id="user_null", text=None)
    clean_db_session.add(user)
    await clean_db_session.commit()
    
    value = await get_user_text(clean_db_session, "user_null")
    assert value is None


@pytest.mark.asyncio
async def test_private_commands_directly(clean_db_session):
    """Test using private commands (get_user_value/set_user_value) directly."""
    # Create user
    user = UserValues(user_id="user_private", text=None)
    clean_db_session.add(user)
    await clean_db_session.commit()
    
    # Set text using private command
    await set_user_value(clean_db_session, "user_private", "text", "Private Value")
    
    # Get text using private command
    value = await get_user_value(clean_db_session, "user_private", "text")
    assert value == "Private Value" 