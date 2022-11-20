"""
Misc utils
"""
import random
import string

from django import http


def get_user_ip(request: http.HttpRequest) -> str:
    """
    Get the IP address of a user
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(",")[0]
    else:
        ip_address = request.META.get("REMOTE_ADDR")
    return ip_address


def random_string(length):
    """
    Generate a random string
    """
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )
