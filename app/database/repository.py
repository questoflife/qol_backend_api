"""
Repository functions for user key-value storage in the Quest of Life Backend API.
Provides async CRUD operations for the UserKeyValue model.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.models import UserKeyValue

async def get_user_key_value(session: AsyncSession, user_id: str, key: str) -> str | None:
    """
    Retrieve the value for a given user's key.
    Returns the value if found, else None.
    """
    result = await session.execute(
        select(UserKeyValue).where(UserKeyValue.user_id == user_id, UserKeyValue.key == key)
    )
    item = result.scalar_one_or_none()
    return item.value if item else None

async def set_user_key_value(session: AsyncSession, user_id: str, key: str, value: str) -> None:
    """
    Set or update the value for a given user's key.
    Creates the key if it does not exist; updates if it does.
    Commits the transaction.
    """
    result = await session.execute(
        select(UserKeyValue).where(UserKeyValue.user_id == user_id, UserKeyValue.key == key)
    )
    item = result.scalar_one_or_none()
    if item:
        item.value = value
    else:
        session.add(UserKeyValue(user_id=user_id, key=key, value=value))
    await session.commit() 