from typing import Any
from sqlalchemy import inspect

from sqlalchemy.exc import SQLAlchemyError

from src.database.errors import DatabaseError, UserNotFoundError, ColumnNotFoundError


async def safe_commit(session) -> None:
    """ Safely commit the current transaction in the session."""
    try:
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        raise DatabaseError("Database operation failed") from e


async def fetch_column(model, column: str) -> Any:
    """Fetch a column dynamically from a SQLAlchemy model."""
    mapper = inspect(model)
    if column not in mapper.columns:
        raise ColumnNotFoundError(model.__name__, column)
    return mapper.columns[column]
