import secrets
import httpx
from fastapi import APIRouter, Request, HTTPException
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse

from src.settings import get_settings

router = APIRouter(prefix="", tags=["auth"])

oauth = OAuth()
oauth.register(
    name="discord",
    client_id=get_settings().DISCORD_CLIENT_ID,
    client_secret=get_settings().DISCORD_CLIENT_SECRET,
    authorize_url="https://discord.com/api/oauth2/authorize",
    access_token_url="https://discord.com/api/oauth2/token",
    client_kwargs={"scope": "identify"},
)


@router.get("/login")
async def login(request: Request):
    # Authlib adds state; PKCE is automatically supported in the client flow
    discord = oauth.create_client("discord")
    if discord is None:
        raise HTTPException(500, "Discord OAuth client not configured")
    redirect_uri = f"{get_settings().API_BASE_URL}/oauth/callback"
    return await discord.authorize_redirect(request, redirect_uri=redirect_uri)


@router.get("/oauth/callback")
async def oauth_callback(request: Request):
    discord = oauth.create_client("discord")
    if discord is None:
        raise HTTPException(500, "Discord OAuth client not configured")
    
    # Exchange code -> tokens
    try:
        token = await discord.authorize_access_token(request)
    except Exception:
        raise HTTPException(status_code=400, detail="OAuth exchange failed")

    # Fetch identity
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        if r.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch Discord user")
        me = r.json()

    discord_id = me["id"]

    # Store session data directly in SessionMiddleware
    request.session["discord_id"] = discord_id
    request.session["csrf"] = secrets.token_urlsafe(32)
    request.session["token_meta"] = token
    
    # Redirect to frontend
    return RedirectResponse(url=f"{get_settings().FRONTEND_ORIGIN}/api-test.html", status_code=303)


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"ok": True}


@router.get("/me")
async def get_current_user(request: Request):
    """
    Get current user info including CSRF token.
    Frontend needs this to get the CSRF token for state-changing requests.
    """
    discord_id = request.session.get("discord_id")
    csrf = request.session.get("csrf")
    
    if not discord_id or not csrf:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    return {
        "discord_id": discord_id,
        "csrf_token": csrf
    }