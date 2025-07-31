"""
Service layer for user key-value operations in the Quest of Life Backend API.
Provides async functions to fetch and set user values using the repository layer.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repository import (
    get_user_key_value as database_get_user_key_value,
    set_user_key_value as database_set_user_key_value,
)

async def get_user_key_value(session: AsyncSession, user_id: str, key: str) -> str | None:
    """
    Business logic for retrieving a user's key-value pair.
    Calls the database layer function.
    """
    return await database_get_user_key_value(session, user_id, key)

async def set_user_key_value(session: AsyncSession, user_id: str, key: str, value: str) -> None:
    """
    Business logic for setting a user's key-value pair.
    Calls the database layer function.
    """
    await database_set_user_key_value(session, user_id, key, value) 