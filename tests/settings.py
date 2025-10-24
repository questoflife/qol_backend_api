"""
Test configuration settings.

Integration tests are designed to run in CI/CD (Northflank) environments.
For local development, run unit tests (test_api.py, test_database.py).

Environment Variables for Integration Tests:
---------------------------------------------

REQUIRED (from src/settings.py):
- FRONTEND_ORIGIN=https://your-app.northflank.app
- API_BASE_URL=https://your-app.northflank.app
- DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET
- SECRET_KEY
- DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

OPTIONAL - Integration Tests:
- RUN_INTEGRATION_TESTS=true
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    """Test-specific configuration."""
    
    RUN_INTEGRATION_TESTS: bool = False


_settings: Optional[TestSettings] = None


def get_test_settings() -> TestSettings:
    """Load test settings from environment."""
    global _settings
    if _settings is None:
        _settings = TestSettings()  # type: ignore[call-arg]
    return _settings
