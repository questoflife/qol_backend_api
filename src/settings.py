from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    # Public site (frontend) and API (this app) live on different domains
    FRONTEND_ORIGIN: AnyHttpUrl
    API_BASE_URL: AnyHttpUrl
    LOGIN_REDIRECT: AnyHttpUrl
    
    # Discord OAuth app credentials
    DISCORD_CLIENT_ID: str
    DISCORD_CLIENT_SECRET: str

    # Security
    SECRET_KEY: str

    # Database
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_SSL_DISABLE_VERIFICATION: bool = False

    @field_validator('FRONTEND_ORIGIN', 'API_BASE_URL', mode='after')
    @classmethod
    def strip_trailing_slash(cls, v):
        """Remove trailing slash from URLs to avoid double-slash issues in path construction."""
        if v is not None:
            return str(v).rstrip('/')
        return v

    @property
    def ASYNC_SERVER_URL(self) -> str:
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings from environment variables. Done this way for lazy import."""
    return Settings()  # loaded from env vars  # type: ignore[call-arg]
