"""
Helper functions for license keys
"""
import random
import string

from api.models import User, Key


def random_string(length):
    """
    Generate a random string
    """
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


def _generate_key():
    return f"LB-{random_string(4)}-{random_string(4)}-{random_string(4)}-{random_string(4)}"


def create_key(user: User = None, key=None, create_reason="", created_by="") -> Key:
    """
    Create a key
    """
    key = Key.objects.create(
        user=user,
        key=key or _generate_key(),
        create_reason=create_reason,
        created_by=created_by,
    )
    if user:
        user.redeemed_key = key
        user.account_type = "Lifetime"
        user.save()
    return key


def is_key_valid(key: str) -> Key:
    """
    Check if a key is valid
    """
    try:
        key: Key = Key.objects.get(key=key)
    except Key.DoesNotExist:
        return None
    if key.redeemed_by is not None:
        return None
    return key
