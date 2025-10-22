"""
End-to-End OAuth tests with browser automation.

These tests are designed to run in CI/CD environments (Northflank) only.
For local development, run unit tests (test_api.py, test_database.py) instead.

Requirements:
- RUN_E2E_TESTS=true
- DISCORD_TEST_EMAIL and DISCORD_TEST_PASSWORD
- FRONTEND_ORIGIN and API_BASE_URL (set to Northflank URL)
- Playwright: included in testing dependencies

The tests start a server on 0.0.0.0:8000 inside the container,
accessible via the public Northflank URL specified in API_BASE_URL.
"""
import pytest
import asyncio
import uvicorn
from playwright.async_api import async_playwright
from httpx import AsyncClient
from src.settings import get_settings
from tests.test_settings import get_test_settings, get_discord_test_credentials


pytestmark = pytest.mark.skipif(
    not get_test_settings().RUN_E2E_TESTS,
    reason="Set RUN_E2E_TESTS=true and provide Discord test credentials"
)


@pytest.fixture(scope="module")
def discord_test_credentials():
    """Get Discord test credentials from environment."""
    return get_discord_test_credentials()


@pytest.fixture(scope="module")
async def backend_server():
    """
    Start backend server for E2E testing on 0.0.0.0:8000.
    Returns API_BASE_URL for browser navigation.
    """
    from src.app import app
    
    api_base_url = str(get_settings().API_BASE_URL)
    
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(server.serve())
    await asyncio.sleep(3)  # Wait for server startup
    
    yield api_base_url
    
    server.should_exit = True
    try:
        await asyncio.wait_for(server_task, timeout=5.0)
    except asyncio.TimeoutError:
        pass


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_full_oauth_flow(backend_server, discord_test_credentials):
    """Test complete OAuth flow with real Discord authentication."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to login
            await page.goto(f"{backend_server}/login")
            await page.wait_for_url("**/discord.com/**", timeout=10000)
            
            # Fill Discord credentials
            await page.wait_for_selector('input[name="email"]', timeout=10000)
            await page.fill('input[name="email"]', discord_test_credentials["email"])
            await page.fill('input[name="password"]', discord_test_credentials["password"])
            await page.click('button[type="submit"]')
            
            # Handle authorize button if present
            await asyncio.sleep(2)
            try:
                authorize_button = page.locator('button:has-text("Authorize"), button:has-text("Autoriser")')
                if await authorize_button.count() > 0:
                    await authorize_button.click(timeout=5000)
            except Exception:
                pass  # Already authorized
            
            # Wait for OAuth callback to complete (redirects to FRONTEND_ORIGIN/welcome)
            try:
                await page.wait_for_url(f"{get_settings().FRONTEND_ORIGIN}/**", timeout=15000)
            except Exception:
                pass  # May land on 404 if /welcome doesn't exist
            
            await asyncio.sleep(1)  # Ensure session is saved
            
            # Verify session cookie
            cookies = await context.cookies()
            session_cookie = next((c for c in cookies if c.get("name") == "qol_session"), None)
            assert session_cookie is not None, "Session cookie should be set"
            cookie_value = session_cookie.get("value")
            assert cookie_value, "Session cookie should have a value"
            
            # Test /me endpoint
            async with AsyncClient(base_url=backend_server) as client:
                client.cookies.set("qol_session", cookie_value)
                
                response = await client.get("/me")
                assert response.status_code == 200
                
                data = response.json()
                assert "discord_id" in data
                assert "csrf_token" in data
                assert data["discord_id"]
                assert data["csrf_token"]
            
        except Exception as e:  
            await page.screenshot(path="test_failure.png")
            raise
        finally:
            await browser.close()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_oauth_with_api_calls(backend_server, discord_test_credentials):
    """Test that session works for authenticated API calls."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Complete OAuth flow
            await page.goto(f"{backend_server}/login")
            await page.wait_for_url("**/discord.com/**", timeout=10000)
            
            await page.wait_for_selector('input[name="email"]', timeout=10000)
            await page.fill('input[name="email"]', discord_test_credentials["email"])
            await page.fill('input[name="password"]', discord_test_credentials["password"])
            await page.click('button[type="submit"]')
            
            await asyncio.sleep(2)
            try:
                authorize_button = page.locator('button:has-text("Authorize"), button:has-text("Autoriser")')
                if await authorize_button.count() > 0:
                    await authorize_button.click(timeout=5000)
            except Exception:
                pass
            
            try:
                await page.wait_for_url(f"{get_settings().FRONTEND_ORIGIN}/**", timeout=15000)
            except Exception:
                pass
            await asyncio.sleep(1)
            
            cookies = await context.cookies()
            session_cookie = next((c for c in cookies if c.get("name") == "qol_session"), None)
            assert session_cookie is not None
            cookie_value = session_cookie.get("value", "")
            assert cookie_value
            
            # Test authenticated API calls
            async with AsyncClient(base_url=backend_server) as client:
                client.cookies.set("qol_session", cookie_value)
                
                me_response = await client.get("/me")
                assert me_response.status_code == 200
                csrf_token = me_response.json()["csrf_token"]
                
                # First create the user in the database
                from src.database.models import UserValues
                from src.database.config import get_app_async_session
                async for session in get_app_async_session():
                    discord_id = me_response.json()["discord_id"]
                    user = UserValues(user_id=discord_id, text=None)
                    session.add(user)
                    await session.commit()
                    break
                
                # Set text with CSRF
                set_response = await client.post(
                    "/user/text",
                    json={"text": "e2e test success"},
                    headers={"X-CSRF-Token": csrf_token}
                )
                assert set_response.status_code == 200
                
                # Get the text back
                get_response = await client.get("/user/text")
                assert get_response.status_code == 200
                assert get_response.json()["text"] == "e2e test success"
                
        finally:
            await browser.close()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_logout_clears_session(backend_server, discord_test_credentials):
    """Test that logout properly clears the session."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Complete OAuth flow
            await page.goto(f"{backend_server}/login")
            await page.wait_for_url("**/discord.com/**", timeout=10000)
            
            await page.wait_for_selector('input[name="email"]', timeout=10000)
            await page.fill('input[name="email"]', discord_test_credentials["email"])
            await page.fill('input[name="password"]', discord_test_credentials["password"])
            await page.click('button[type="submit"]')
            
            await asyncio.sleep(2)
            try:
                authorize_button = page.locator('button:has-text("Authorize"), button:has-text("Autoriser")')
                if await authorize_button.count() > 0:
                    await authorize_button.click(timeout=5000)
            except Exception:
                pass
            
            try:
                await page.wait_for_url(f"{get_settings().FRONTEND_ORIGIN}/**", timeout=15000)
            except Exception:
                pass
            await asyncio.sleep(1)
            
            cookies = await context.cookies()
            session_cookie = next((c for c in cookies if c.get("name") == "qol_session"), None)
            assert session_cookie is not None
            cookie_value = session_cookie.get("value", "")
            assert cookie_value
            
            async with AsyncClient(base_url=backend_server) as client:
                client.cookies.set("qol_session", cookie_value)
                
                # Verify logged in
                me_response = await client.get("/me")
                assert me_response.status_code == 200
                
                # Logout
                logout_response = await client.post("/logout")
                assert logout_response.status_code == 200
                
                # Verify logged out
                me_response_after = await client.get("/me")
                assert me_response_after.status_code == 401
                
        finally:
            await browser.close()

