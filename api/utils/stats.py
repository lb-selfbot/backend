"""
Statistics
"""
import time
import psutil

from django.db.models import Sum

from ..utils import misc, releases
from ..models import User


def all_stats(user: User) -> dict:
    """
    Get all stats
    """
    latest_release = releases.get_latest("selfbot")

    latest_version = latest_release.version if latest_release else "Unknown"

    stats = {
        "auth": "Online",
        "version": latest_version,
        "users": User.objects.count(),
        "logins": User.objects.aggregate(Sum("logins"))["logins__sum"],
        "hosting": User.objects.filter(is_hosting=True).count(),
    }

    if user.is_staff or user.is_superuser:
        stats["admin"] = admin_stats()

    return stats


def admin_stats() -> dict:
    """
    Get administrator stats
    """

    virtual_memory = psutil.virtual_memory()

    used_gb = virtual_memory.used / 1024**3
    total_gb = virtual_memory.total / 1024**3

    uptime_seconds = time.time() - psutil.boot_time()

    return {
        "cpu": f"{psutil.cpu_percent()}%",
        "ram": f"{virtual_memory.percent}% ({used_gb:.2f}GB / {total_gb:.2f}GB)",
        "rpm": str(misc.get_rpm()),
        "uptime": misc.seconds_to_readable_time(uptime_seconds),
    }
