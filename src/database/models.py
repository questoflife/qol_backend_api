"""
SQLAlchemy models for the Quest of Life Backend API.
Defines the database schema for user key-value storage.
"""
from sqlalchemy import String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    """
    Declarative base class for all models.
    """
    pass


class UserValues(BaseModel):
    """
    SQLAlchemy model for storing values for each user, indexed by the user. 
    """
    __tablename__ = "user_values"
    user_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=True)
