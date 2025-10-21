"""
Pydantic schemas for request and response validation in the Quest of Life Backend API.
"""
from pydantic import BaseModel

class Text(BaseModel):
    """
    Request schema for setting or getting a user text.
    """
    text: str
