"""
Pydantic schemas for request and response validation in the Quest of Life Backend API.
"""
from pydantic import BaseModel

class KeyValueIn(BaseModel):
    """
    Request schema for setting a user key-value pair.
    """
    key: str
    value: str

class KeyValueOut(BaseModel):
    """
    Response schema for returning a user key-value pair.
    """
    key: str
    value: str 