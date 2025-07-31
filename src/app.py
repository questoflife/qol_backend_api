"""
Main FastAPI application for the Quest of Life Backend API.
Defines API endpoints and wires dependencies.
"""
from fastapi import FastAPI
from src.api.user_dict import router as user_dict_router

app = FastAPI()

app.include_router(user_dict_router)
