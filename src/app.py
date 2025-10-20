"""
Main FastAPI application for the Quest of Life Backend API.
Defines API endpoints and wires dependencies.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from starlette.middleware.sessions import SessionMiddleware

from src.api.sessions import InMemorySessionStore
from src.settings import get_settings
from src.api.auth import router as auth_router
from src.api.user_dict import router as user_dict_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.session_store = InMemorySessionStore()
    await app.state.session_store.start()
    yield
    # Shutdown
    await app.state.session_store.stop()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(get_settings().FRONTEND_ORIGIN)],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", get_settings().CSRF_HEADER_NAME],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=get_settings().SECRET_KEY,
    https_only=True,
    same_site="none",
    max_age=60*15, # 15 minutes
)



app.include_router(auth_router)
app.include_router(user_dict_router)
