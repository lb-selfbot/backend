"""
Helper functions for releases
"""
from ..models import Release


def get_latest(branch: str) -> Release:
    """
    Get the latest release
    """
    try:
        return Release.objects.filter(branch=branch).latest("created_at")
    except Release.DoesNotExist:
        return None
