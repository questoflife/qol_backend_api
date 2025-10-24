"""
Repository functions for user key-value storage in the Quest of Life Backend API.
Provides async CRUD operations for the UserKeyValue model.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.private_commands import get_user_value, set_user_value

async def get_user_text(session: AsyncSession, user_id: str) -> str | None:
    return await get_user_value(session, user_id, "text")

async def set_user_text(session: AsyncSession, user_id: str, text: str) -> None:
    await set_user_value(session, user_id, "text", text)
