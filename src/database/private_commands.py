from typing import Any, Type
from xml.parsers.expat import model
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute

from src.database.errors import DatabaseError, UserNotFoundError, ColumnNotFoundError
from src.database.models import UserValues, BaseModel
from src.database.helpers import safe_commit, fetch_column


async def get_user_value(session: AsyncSession, user_id: str, column: str) -> Any | None:
    """ Retrieve any value from UserValues"""
    await fetch_column(UserValues, column)  # Validate column exists
    row = await session.get(UserValues, user_id)
    if not row:
        raise UserNotFoundError(user_id)
    return getattr(row, column)


async def set_user_value(session: AsyncSession, user_id: str, column: str, value: Any) -> None:
    """ Set any value in UserValues """
    await fetch_column(UserValues, column)  # Validate column exists
    row = await session.get(UserValues, user_id)
    if not row:
        raise UserNotFoundError(user_id)
    setattr(row, column, value)
    await safe_commit(session)