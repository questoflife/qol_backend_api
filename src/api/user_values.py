"""
User dictionary API routes for the Quest of Life Backend API.
Provides endpoints for getting and setting user key-value pairs.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_discord_id, require_csrf
from src.database.config import get_app_async_session
from src.api.schemas import Text
from src.backend.commands import get_user_text, set_user_text

router = APIRouter()

@router.get("/user/text", response_model=Text)
async def get_user_value(
    session: AsyncSession = Depends(get_app_async_session),
    user_id: str = Depends(get_current_discord_id),
) -> Text:
    """
    Get the stored text for the current user.
    """
    value = await get_user_text(session, user_id)
    value = value if value is not None else ""
    return Text(text=value)

@router.post("/user/text", response_model=Text)
async def set_user_value(
    payload: Text,
    session: AsyncSession = Depends(get_app_async_session),
    user_id: str = Depends(get_current_discord_id),
    _: bool = Depends(require_csrf),
) -> Text:
    """
    Set the stored text for the current user.
    """
    await set_user_text(session, user_id, payload.text)
    return Text(text=payload.text)
