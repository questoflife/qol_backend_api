"""
Main FastAPI application for the Quest of Life Backend API.
Defines API endpoints and wires dependencies.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.settings import get_settings
from src.api.deps import limiter
from src.api.auth import router as auth_router
from src.api.user_values import router as user_values_router
from src.database.config import create_test_tables_if_not_exist, get_app_async_session
from src.database.errors import DatabaseError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan: runs on startup and shutdown.
    Creates database tables on startup if they don't exist.
    """
    # Startup: create tables if they don't exist
    await create_test_tables_if_not_exist()
    
    yield
    
    # Shutdown: nothing to do


app = FastAPI(lifespan=lifespan)

# Add rate limiter state and exception handler
# Note: app.state.limiter is required by slowapi to access the limiter instance
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]


@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError):
    """Handle database errors gracefully with user-friendly messages."""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Database operation failed with exception {exc}. Please try again."}
    )


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Always apply these security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    
    # Apply strict cache control to sensitive endpoints (user data, auth)
    # Skip for future public/static endpoints (health checks, docs, etc.)
    sensitive_paths = ["/user/", "/me", "/logout", "/oauth/"]
    if any(path in request.url.path for path in sensitive_paths):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    else:
        # For other endpoints, allow short-term caching (e.g., health checks)
        response.headers["Cache-Control"] = "public, max-age=60"
    
    return response


@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Limit request body size to prevent DoS attacks."""
    content_length = request.headers.get("content-length")
    
    # Check if Content-Length is present (some attacks omit it)
    if content_length:
        try:
            if int(content_length) > 50_000:  # 50KB limit - generous for 10KB text + JSON overhead
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request too large. Maximum size: 50KB"}
                )
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid Content-Length header"}
            )
    elif request.method in ["POST", "PUT", "PATCH"]:
        # For state-changing requests, require Content-Length header
        # (Prevents chunked encoding attacks without length specified)
        if request.headers.get("transfer-encoding") != "chunked":
            return JSONResponse(
                status_code=411,
                content={"detail": "Content-Length header required"}
            )
    
    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(get_settings().FRONTEND_ORIGIN)],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=get_settings().SECRET_KEY,
    session_cookie="qol_session",
    https_only=True,
    same_site="none",  # Required for cross-domain (API ≠ frontend domain). CSRF protection is CRITICAL!
    max_age=4 * 60 * 60,  # 4 hours - balance between security and UX
)


app.include_router(auth_router)
app.include_router(user_values_router)


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and container orchestration."""
    return {"status": "healthy"}


@app.get("/readiness")
async def readiness_check(session: AsyncSession = Depends(get_app_async_session)):
    """Readiness check - verifies database connectivity."""
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "detail": "Database unavailable"}
        )
