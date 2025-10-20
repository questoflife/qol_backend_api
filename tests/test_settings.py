"""
Test configuration settings.

Environment Variables for Testing:
----------------------------------

REQUIRED (from src/settings.py):
- FRONTEND_ORIGIN, API_BASE_URL
- DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET
- SECRET_KEY
- DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

OPTIONAL - Integration Tests:
- RUN_INTEGRATION_TESTS=true

OPTIONAL - E2E Tests (browser automation):
- RUN_E2E_TESTS=true
- DISCORD_TEST_EMAIL=your-test@email.com
- DISCORD_TEST_PASSWORD=your-test-password
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    """Test-specific configuration."""
    
    RUN_INTEGRATION_TESTS: bool = False
    RUN_E2E_TESTS: bool = False
    DISCORD_TEST_EMAIL: Optional[str] = None
    DISCORD_TEST_PASSWORD: Optional[str] = None


_settings: Optional[TestSettings] = None


def get_test_settings() -> TestSettings:
    """Load test settings from environment."""
    global _settings
    if _settings is None:
        _settings = TestSettings()  # type: ignore[call-arg]
    return _settings


def get_discord_test_credentials() -> dict[str, str]:
    """Get Discord test account credentials."""
    settings = get_test_settings()
    
    if settings.RUN_E2E_TESTS and (not settings.DISCORD_TEST_EMAIL or not settings.DISCORD_TEST_PASSWORD):
        raise ValueError("E2E tests require DISCORD_TEST_EMAIL and DISCORD_TEST_PASSWORD")
    
    return {
        "email": settings.DISCORD_TEST_EMAIL or "",
        "password": settings.DISCORD_TEST_PASSWORD or ""
    }

