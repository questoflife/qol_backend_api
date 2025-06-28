from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.models import UserKeyValue

async def get_user_key_value(session: AsyncSession, user_id: str, key: str) -> str | None:
    result = await session.execute(
        select(UserKeyValue).where(UserKeyValue.user_id == user_id, UserKeyValue.key == key)
    )
    item = result.scalar_one_or_none()
    return item.value if item else None

async def set_user_key_value(session: AsyncSession, user_id: str, key: str, value: str) -> None:
    result = await session.execute(
        select(UserKeyValue).where(UserKeyValue.user_id == user_id, UserKeyValue.key == key)
    )
    item = result.scalar_one_or_none()
    if item:
        item.value = value
    else:
        session.add(UserKeyValue(user_id=user_id, key=key, value=value))
    await session.commit() 