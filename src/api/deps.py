from fastapi import HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address


# Initialize single rate limiter instance for the entire application
limiter = Limiter(key_func=get_remote_address)


async def get_current_discord_id(request: Request) -> str:
    """
    Dependency to get the current authenticated user's Discord ID.
    SessionMiddleware automatically validates the cookie signature.
    """
    discord_id = request.session.get("discord_id")
    if not discord_id:
        raise HTTPException(status_code=401, detail="Not logged in")
    return discord_id


async def require_csrf(request: Request) -> bool:
    """
    Dependency for state-changing requests (POST/PUT/DELETE/PATCH).
    Validates that the CSRF token in the header matches the one in the session.
    This prevents cross-site request forgery attacks.
    """
    session_csrf = request.session.get("csrf")
    header_csrf = request.headers.get("X-CSRF-Token")
    
    if not session_csrf or not header_csrf:
        raise HTTPException(status_code=403, detail="Missing CSRF token")
    
    if session_csrf != header_csrf:
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
    
    return True