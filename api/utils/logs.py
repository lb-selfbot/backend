"""
Logging utilities
"""

from ..models import User, Log


def create_entry(log_type: str, user: User, info: dict) -> Log:
    """
    Create a log entry
    """

    return Log.objects.create(log_type=log_type, user=user, info=info)
