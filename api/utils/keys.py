"""
Helper functions for license keys
"""
import random
import string

from api.models import User, Key, CreditKey
from api.utils import misc, logs


def _generate_key() -> str:
    random_strings = [misc.random_string(4) for _ in range(4)]

    return "LB-" + "-".join(random_strings)


def create_key(user: User = None, key=None, create_reason="", created_by="") -> Key:
    """
    Create a key
    """
    key = Key.objects.create(
        key=key or _generate_key(),
        created_by=created_by,
        create_reason=create_reason,
        redeemed_by=user,
    )

    if user:
        user.redeemed_key = key
        user.account_type = "Premium"
        user.hosting_credit += 5 * 24 * 60  # 1 month
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


def create_credit_key(create_reason="", created_by="", credit_amount=0, is_lifetime=False) -> CreditKey:
    """
    Create a credit key
    """
    key = CreditKey.objects.create(
        key=_generate_key(),
        created_by=created_by,
        create_reason=create_reason,
        is_lifetime=is_lifetime,
        credit_amount=credit_amount,
    )

    logs.create_entry(
        log_type="create_credit_key",
        user=None,
        info={
            "key": key.key,
            "create_reason": create_reason,
            "created_by": created_by,
            "credit_amount": credit_amount,
            "is_lifetime": is_lifetime,
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


def get_credit_key(key: str) -> CreditKey:
    """
    Get a credit key
    """
    try:
        return CreditKey.objects.get(key=key)
    except CreditKey.DoesNotExist:
        return None


def get_key_if_unredeemed(key: str) -> Key:
    """
    Check if a key is valid
    """
    key = get_key(key)

    if key and not key.redeemed_by:
        return key

    return None


def get_credit_key_if_unredeemed(key: str) -> CreditKey:
    """
    Check if a credit key is valid
    """
    key = get_credit_key(key)

    if key and not key.redeemed_by:
        return key

    return None
