"""
Pydantic schemas for request and response validation in the Quest of Life Backend API.
"""
from pydantic import BaseModel, Field, field_validator


class Text(BaseModel):
    """
    Request schema for setting or getting a user text.
    Includes security validations to prevent abuse.
    """
    text: str = Field(
        max_length=10_000,  # 10KB text limit
        description="User text content (max 10KB)"
    )
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        """
        Validate and sanitize text input.
        """
        # Strip leading/trailing whitespace
        v = v.strip()
        
        # Check for null bytes or other problematic characters
        if '\x00' in v:
            raise ValueError('Text contains invalid null bytes')
        
        # Check for excessive control characters (allow newlines and tabs)
        control_chars = sum(1 for c in v if ord(c) < 32 and c not in '\n\t\r')
        if control_chars > 10:  # Allow some control chars but not excessive amounts
            raise ValueError('Text contains too many control characters')
        
        return v
