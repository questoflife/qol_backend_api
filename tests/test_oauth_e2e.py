"""
End-to-End OAuth tests with browser automation.
Skipped by default. Requires:
- RUN_E2E_TESTS=true
- DISCORD_TEST_EMAIL and DISCORD_TEST_PASSWORD
- Playwright: pip install playwright && playwright install chromium

See tests/test_settings.py for configuration.
"""
import pytest
import asyncio
import uvicorn
from playwright.async_api import async_playwright
from httpx import AsyncClient
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
    """Start backend server for E2E testing."""
    from src.app import app
    
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(server.serve())
    await asyncio.sleep(3)  # Wait for server startup
    
    yield "http://127.0.0.1:8000"
    
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
                # Authorize button may not appear if already authorized
                pass
            
            # Wait for redirect to frontend
            from src.settings import get_settings
            frontend_origin = str(get_settings().FRONTEND_ORIGIN)
            await page.wait_for_url(f"{frontend_origin}/**", timeout=15000)
            
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
                # Authorize button may not appear if already authorized
                pass
            
            from src.settings import get_settings
            await page.wait_for_url(f"{get_settings().FRONTEND_ORIGIN}/**", timeout=15000)
            
            cookies = await context.cookies()
            session_cookie = next((c for c in cookies if c.get("name") == "qol_session"), None)
            assert session_cookie is not None, "Session cookie should be set"
            cookie_value = session_cookie.get("value")
            assert cookie_value, "Session cookie should have a value"
            
            # Test authenticated API calls
            async with AsyncClient(base_url=backend_server) as client:
                client.cookies.set("qol_session", cookie_value)
                
                me_response = await client.get("/me")
                assert me_response.status_code == 200
                csrf_token = me_response.json()["csrf_token"]
                
                # Set a value with CSRF
                set_response = await client.post(
                    "/user/dict",
                    json={"key": "e2e_test", "value": "success"},
                    headers={"X-CSRF-Token": csrf_token}
                )
                assert set_response.status_code == 200
                
                # Get the value back
                get_response = await client.get("/user/dict/e2e_test")
                assert get_response.status_code == 200
                assert get_response.json()["value"] == "success"
                
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
                # Authorize button may not appear if already authorized
                pass
            
            from src.settings import get_settings
            await page.wait_for_url(f"{get_settings().FRONTEND_ORIGIN}/**", timeout=15000)
            
            cookies = await context.cookies()
            session_cookie = next((c for c in cookies if c.get("name") == "qol_session"), None)
            assert session_cookie is not None, "Session cookie should be set"
            cookie_value = session_cookie.get("value")
            assert cookie_value, "Session cookie should have a value"
            
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

