from fastapi import HTTPException, Request
from src.settings import get_settings

async def get_current_user_id(request: Request) -> str:
    sid = request.cookies.get(get_settings().SESSION_COOKIE_NAME)
    if not sid:
        raise HTTPException(status_code=401, detail="Not logged in")
    store = request.app.state.session_store
    session = await store.get(sid)
    if not session:
        raise HTTPException(status_code=401, detail="Session expired")
    # Optional: sliding expiration
    await store.touch(sid)
    request.state.session = session  # stash if handlers need more info
    return session["user_id"]

def require_csrf(request: Request):
    # For state-changing requests (POST/PUT/DELETE/PATCH)
    sid = request.cookies.get(get_settings().SESSION_COOKIE_NAME)
    if not sid:
        raise HTTPException(status_code=401, detail="Not logged in")
    store = request.app.state.session_store

    async def _inner():
        session = await store.get(sid)
        if not session:
            raise HTTPException(status_code=401, detail="Session expired")
        incoming = request.headers.get(get_settings().CSRF_HEADER_NAME)
        if not incoming or incoming != session.get("csrf"):
            raise HTTPException(status_code=403, detail="Bad CSRF token")
        # (Optional) rotate CSRF here
        request.state.session = session
        return True

    return _inner