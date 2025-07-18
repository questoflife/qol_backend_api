"""
Main FastAPI application for the Quest of Life Backend API.
Defines API endpoints and wires dependencies.
"""
from fastapi import FastAPI
from app.api.routes.user_dict import router as user_dict_router

app = FastAPI()

app.include_router(user_dict_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
