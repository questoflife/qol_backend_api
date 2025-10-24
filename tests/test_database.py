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
async def test_get_nonexistent_user_auto_creates(clean_db_session):
    """Test getting text for a user that doesn't exist auto-creates the user."""
    value = await get_user_value(clean_db_session, "nonexistent_user", "text")
    assert value is None
    
    # Verify the user was created
    result = await clean_db_session.execute(
        select(UserValues).where(UserValues.user_id == "nonexistent_user")
    )
    user_records = result.scalars().all()
    assert len(user_records) == 1
    assert user_records[0].text is None


@pytest.mark.asyncio
async def test_set_nonexistent_user_auto_creates(clean_db_session):
    """Test setting text for a user that doesn't exist auto-creates the user."""
    await set_user_value(clean_db_session, "new_user", "text", "some value")
    
    # Verify the user was created and value was set
    value = await get_user_value(clean_db_session, "new_user", "text")
    assert value == "some value"


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
    # Set text using private command (should auto-create user)
    await set_user_value(clean_db_session, "user_private", "text", "Private Value")
    
    # Get text using private command
    value = await get_user_value(clean_db_session, "user_private", "text")
    assert value == "Private Value"


@pytest.mark.asyncio
async def test_auto_create_on_get_then_set(clean_db_session):
    """Test that auto-created user on get can then be updated with set."""
    # First access via get (auto-creates with None)
    value = await get_user_value(clean_db_session, "auto_user", "text")
    assert value is None
    
    # Now set a value
    await set_user_value(clean_db_session, "auto_user", "text", "Updated")
    
    # Verify it was updated
    value = await get_user_value(clean_db_session, "auto_user", "text")
    assert value == "Updated"
    
    # Verify only one record exists
    result = await clean_db_session.execute(
        select(UserValues).where(UserValues.user_id == "auto_user")
    )
    user_records = result.scalars().all()
    assert len(user_records) == 1 