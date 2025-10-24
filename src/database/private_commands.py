from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.database.models import UserValues
from src.database.helpers import safe_commit, fetch_column


async def ensure_user_values_exists(session: AsyncSession, user_id: str) -> None:
    """
    Ensure that a UserValues row exists for the given user_id.
    If the user doesn't exist, create a new row with all columns initialized to None.
    Handles race conditions when multiple concurrent requests try to create the same user.
    """
    row = await session.get(UserValues, user_id)
    if not row:
        new_user = UserValues(user_id=user_id, text=None)
        session.add(new_user)
        try:
            await session.flush()
        except IntegrityError:
            # Another concurrent request created the user first - that's ok
            # Rollback and refresh to get the existing row
            await session.rollback()
            # The row now exists, we can continue normally


async def get_user_value(session: AsyncSession, user_id: str, column: str) -> Any | None:
    """Retrieve any value from UserValues"""
    await fetch_column(UserValues, column)  # Validate column exists
    await ensure_user_values_exists(session, user_id)
    await safe_commit(session)  # Commit the auto-created user if needed
    row = await session.get(UserValues, user_id)
    return getattr(row, column)


async def set_user_value(session: AsyncSession, user_id: str, column: str, value: Any) -> None:
    """Set any value in UserValues"""
    await fetch_column(UserValues, column)  # Validate column exists
    await ensure_user_values_exists(session, user_id)
    row = await session.get(UserValues, user_id)
    setattr(row, column, value)
    await safe_commit(session)  # Commit both user creation and value update