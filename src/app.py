"""
Main FastAPI application for the Quest of Life Backend API.
Defines API endpoints and wires dependencies.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from starlette.middleware.sessions import SessionMiddleware

from src.settings import get_settings
from src.api.auth import router as auth_router
from src.api.user_dict import router as user_dict_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(get_settings().FRONTEND_ORIGIN)],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
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
app.include_router(user_dict_router)
