"""
SQLAlchemy models for the Quest of Life Backend API.
Defines the database schema.
"""
from sqlalchemy import String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Declarative base class for all models.
    """
    pass

class UserKeyValue(Base):
    """
    SQLAlchemy model for storing user-specific key-value pairs.
    Composite primary key: (user_id, key)
    """
    __tablename__ = "user_key_value"
    user_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[str] = mapped_column(Text) 