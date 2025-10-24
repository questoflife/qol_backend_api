class DatabaseError(Exception):
    """Custom exception raised for general database errors."""
    pass

class UserNotFoundError(Exception):
    """Custom exception raised when a user is not found in the database."""
    def __init__(self, user: str) -> None:
        return super().__init__(f"User with ID {user} not found.")


class ColumnNotFoundError(Exception):
    """Custom exception raised when a specified column is not found in a model."""
    def __init__(self, model: str, column: str) -> None:
        return super().__init__(f"Column '{column}' not found in model '{model}'.")