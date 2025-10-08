"""
Main FastAPI application for the Quest of Life Backend API.
Defines API endpoints and wires dependencies.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  
from src.api.user_dict import router as user_dict_router

app = FastAPI()

# CORS configuration
origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(user_dict_router)
