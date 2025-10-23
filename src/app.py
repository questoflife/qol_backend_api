"""
Main FastAPI application for the Quest of Life Backend API.
Defines API endpoints and wires dependencies.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from starlette.middleware.sessions import SessionMiddleware

from src.settings import get_settings
from src.api.auth import router as auth_router
from src.api.user_values import router as user_values_router
from src.database.config import create_test_tables_if_not_exist


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
    same_site="none",
    max_age=14 * 24 * 60 * 60,  # 14 days
)


app.include_router(auth_router)
app.include_router(user_values_router)
