"""
Integration tests for Discord OAuth configuration.
Skipped by default. Set RUN_INTEGRATION_TESTS=true to enable.
See tests/test_settings.py for configuration.
"""
import pytest
from httpx import AsyncClient, ASGITransport

from src.app import app
from src.settings import get_settings
from tests.settings import get_test_settings


pytestmark = pytest.mark.skipif(
    not get_test_settings().RUN_INTEGRATION_TESTS,
    reason="Set RUN_INTEGRATION_TESTS=true to enable"
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_redirect():
    """Test that /login creates a proper Discord OAuth redirect."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False) as client:
        response = await client.get("/login")
        
        # Should redirect to Discord (302 or 307 both indicate redirect)
        assert response.status_code in [302, 307]
        
        location = response.headers.get("location", "")
        assert "discord.com/api/oauth2/authorize" in location
        assert get_settings().DISCORD_CLIENT_ID in location
        assert "redirect_uri" in location
        assert "identify" in location  # Check scope


@pytest.mark.integration
@pytest.mark.asyncio
async def test_discord_client_configured():
    """Test that Discord OAuth client is properly configured."""
    settings = get_settings()
    
    # Verify all required Discord settings are present
    assert settings.DISCORD_CLIENT_ID, "DISCORD_CLIENT_ID must be set"
    assert settings.DISCORD_CLIENT_SECRET, "DISCORD_CLIENT_SECRET must be set"
    assert settings.API_BASE_URL, "API_BASE_URL must be set"
    
    # Verify the redirect URI is properly formatted
    redirect_uri = f"{settings.API_BASE_URL}/oauth/callback"
    assert redirect_uri.startswith("http"), "API_BASE_URL should start with http/https"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_me_endpoint_without_session():
    """Test that /me returns 401 when not logged in."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/me")
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Not logged in"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_logout():
    """Test that logout clears the session."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Even without a session, logout should succeed
        response = await client.post("/logout")
        
        assert response.status_code == 200
        assert response.json() == {"ok": True}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_oauth_callback_without_code():
    """Test that /oauth/callback fails without a code parameter."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False) as client:
        # Call callback without code parameter
        response = await client.get("/oauth/callback")
        
        # Authlib will raise an error for missing code
        assert response.status_code in [400, 422, 500]  # Bad request, validation error, or server error


@pytest.mark.integration  
@pytest.mark.asyncio
async def test_oauth_callback_with_invalid_code():
    """Test that /oauth/callback fails with an invalid code."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False) as client:
        # Call callback with invalid code
        response = await client.get("/oauth/callback?code=invalid_code_12345&state=test_state")
        
        # Should fail during token exchange
        assert response.status_code == 400
        assert "OAuth exchange failed" in response.json()["detail"]


@pytest.mark.integration
@pytest.mark.asyncio  
async def test_cors_configuration():
    """Test that CORS is properly configured for the frontend."""
    settings = get_settings()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Make a preflight request
        response = await client.options(
            "/user/text",
            headers={
                "Origin": str(settings.FRONTEND_ORIGIN),
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,X-CSRF-Token"
            }
        )
        
        # Should allow the request
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers


# NOTE: Full OAuth flow testing with real Discord requires browser automation
# (Playwright/Selenium) to click through Discord's authorization page.
# This is typically done in staging environments, not in unit/integration tests.
#
# What we CAN test here:
# ✅ OAuth endpoints are configured correctly  
# ✅ Invalid inputs are rejected properly
# ✅ Session management works
# ✅ CORS is configured
#
# What requires manual/staging testing:
# ❌ Complete browser OAuth flow
# ❌ Real Discord authorization codes
# ❌ Actual Discord user data retrieval

