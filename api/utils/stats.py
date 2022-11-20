"""
Statistics
"""
from django.db.models import Sum

from ..models import User


def all_stats():
    """
    Get all stats
    """
    return {
        "auth": "Online",
        "version": "4.0.0",  # TODO: Get from db
        "users": User.objects.count(),
        "logins": User.objects.aggregate(Sum("logins"))["logins__sum"],
    }
