from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.auth import get_current_user
from app.database.config import get_app_async_session
from app.api.schemas import KeyValueIn, KeyValueOut
from app.backend.service import fetch_user_value, set_user_value

router = APIRouter()

@router.get("/user/dict/{key}", response_model=KeyValueOut)
async def get_user_value(
    key: str,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_app_async_session)
) -> KeyValueOut:
    value = await fetch_user_value(session, current_user, key)
    if value is None:
        return KeyValueOut(key=key, value="")
    return KeyValueOut(key=key, value=value)

@router.post("/user/dict", response_model=None)
async def set_user_value_endpoint(
    payload: KeyValueIn,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_app_async_session)
):
    await set_user_value(session, current_user, payload.key, payload.value)
    return {"message": "Value set successfully."} 