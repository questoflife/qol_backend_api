import httpx
from fastapi import APIRouter, Request, Response, HTTPException
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse

from src import settings
from src.settings import get_settings
from src.api.sessions import SessionStore

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

def set_session_cookie(response: Response, sid: str) -> None:
    """ Cross-site cookie for different frontend domain"""
    response.set_cookie(
        key=get_settings().SESSION_COOKIE_NAME,
        value=sid,
        max_age=get_settings().SESSION_TTL_SECONDS,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        domain=None
    )

def clear_session_cookie(response: Response) -> None:
    """ Clear session cookie """
    response.delete_cookie(
        key=get_settings().SESSION_COOKIE_NAME,
        path="/",
        domain=None
    )


@router.get("/login")
async def login(request: Request):
    # Authlib adds state; PKCE is automatically supported in the client flow
    discord = oauth.create_client("discord")
    if discord is None:
        raise HTTPException(500, "Discord OAuth client not configured")
    redirect_uri = f"{get_settings().API_BASE_URL}{get_settings().DISCORD_REDIRECT_PATH}"
    return await discord.authorize_redirect(request, redirect_uri=redirect_uri)


@router.get(get_settings().DISCORD_REDIRECT_PATH)
async def oauth_callback(request: Request, response: Response):
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

    # Create server-side session in Redis
    store: SessionStore = request.app.state.session_store
    sid = await store.create(user_id=discord_id, discord_id=discord_id, token_meta=token)

    # Set cookie and bounce back to your frontend
    set_session_cookie(response, sid)
    # Redirect to frontend (maybe a /dashboard)
    return RedirectResponse(url=f"{get_settings().FRONTEND_ORIGIN}/welcome", status_code=303)


@router.post("/logout")
async def logout(request: Request, response: Response):
    sid = request.cookies.get(get_settings().SESSION_COOKIE_NAME)
    if sid:
        await request.app.state.session_store.destroy(sid)
    clear_session_cookie(response)
    return {"ok": True}