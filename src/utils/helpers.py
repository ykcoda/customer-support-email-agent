"""Utility helper functions."""

import uuid
from datetime import datetime


def generate_email_id() -> str:
    """
    Generate a unique email ID.

    Returns:
        str: Unique email ID
    """
    return f"email_{uuid.uuid4().hex[:12]}"


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format.

    Returns:
        str: Current timestamp
    """
    return datetime.utcnow().isoformat()


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to specified length.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


# TODO: Add more helper functions as needed
