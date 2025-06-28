from sqlalchemy.ext.asyncio import AsyncSession
from app.database.repository import get_user_key_value, set_user_key_value

async def fetch_user_value(session: AsyncSession, user_id: str, key: str) -> str | None:
    return await get_user_key_value(session, user_id, key)

async def set_user_value(session: AsyncSession, user_id: str, key: str, value: str) -> None:
    await set_user_key_value(session, user_id, key, value) 