"""
User dictionary API routes for the Quest of Life Backend API.
Provides endpoints for getting and setting user key-value pairs.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.auth import get_current_user
from src.database.config import get_app_async_session
from src.api.schemas import KeyValueIn, KeyValueOut
from src.backend.service import get_user_key_value, set_user_key_value

router = APIRouter()

@router.get("/user/dict/{key}", response_model=KeyValueOut)
async def get_user_value(
    key: str,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_app_async_session)
) -> KeyValueOut:
    """
    Get the value for a given key for the current user.
    Returns an empty value if the key does not exist.
    """
    value = await get_user_key_value(session, current_user, key)
    if value is None:
        return KeyValueOut(key=key, value="")
    return KeyValueOut(key=key, value=value)

@router.post("/user/dict", response_model=None)
async def set_user_value_endpoint(
    payload: KeyValueIn,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_app_async_session)
):
    """
    Set or update the value for a given key for the current user.
    Returns a success message on completion.
    """
    await set_user_key_value(session, current_user, payload.key, payload.value)
    return {"message": "Value set successfully."} 