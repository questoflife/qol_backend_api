"""
Pydantic schemas for request and response validation in the Quest of Life Backend API.
"""
from pydantic import BaseModel

class KeyValueIn(BaseModel):
    key: str
    value: str

class KeyValueOut(BaseModel):
    key: str
    value: str 