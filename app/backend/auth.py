"""
Authentication utilities for the Quest of Life Backend API.
Currently uses a mock user for development/testing.
"""
def get_current_user() -> str:
    """
    Mock authentication dependency.
    Returns a fixed user ID for all requests.
    Replace with real Discord OAuth2 logic in production.
    """
    return "mock_user_id" 