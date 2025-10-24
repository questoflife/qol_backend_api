"""
Service layer for user key-value operations in the Quest of Life Backend API.
Provides async functions to fetch and set user values using the repository layer.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.commands import (
    get_user_text as database_get_user_text,
    set_user_text as database_set_user_text,
)

async def get_user_text(session: AsyncSession, user_id: str) -> str | None:
    """ Calls the database layer function. """
    return await database_get_user_text(session, user_id)

async def set_user_text(session: AsyncSession, user_id: str, text: str) -> None:
    """ Calls the database layer function. """
    await database_set_user_text(session, user_id, text)

