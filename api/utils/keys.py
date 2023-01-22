"""
Helper functions for license keys
"""
import random
import string

from api.models import User, Key
from api.utils import misc, logs


def _generate_key() -> str:
    random_strings = [misc.random_string(4) for _ in range(4)]

    return "LB-" + "-".join(random_strings)


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
        user.account_type = "Premium"
        user.save()

    logs.create_entry(
        log_type="create_key",
        user=user,
        info={
            "key": key.key,
            "create_reason": create_reason,
            "created_by": created_by,
            "redeem_user": getattr(user, "username", None),
        },
    )

    return key


def get_key(key: str) -> Key:
    """
    Get a key
    """
    try:
        return Key.objects.get(key=key)
    except Key.DoesNotExist:
        return None


def get_key_if_unredeemed(key: str) -> Key:
    """
    Check if a key is valid
    """
    key = get_key(key)

    if key and not key.redeemed_by:
        return key

    return None
