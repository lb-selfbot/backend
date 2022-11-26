"""
Models for the Django ORM
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model
    """

    is_tester = models.BooleanField(default=False)
    account_type = models.CharField(max_length=64, default="None")
    free_trial_expiry = models.BigIntegerField(default=0)
    last_selfbot_login = models.DateTimeField(blank=True, null=True)
    logins = models.IntegerField(default=0)
    heartbeats = models.IntegerField(default=0)
    login_time = models.BigIntegerField(default=0)
    hwid = models.CharField(max_length=255, default="")
    hwid_resets = models.JSONField(default=list)
    redeemed_key = models.ForeignKey(
        "Key", on_delete=models.CASCADE, null=True, blank=True
    )


class PasswordResetToken(models.Model):
    """
    Password reset token model
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.BigIntegerField(default=0)


class Order(models.Model):
    """
    Order model
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=64, default="")
    order_id = models.CharField(max_length=255, default="")
    key = models.CharField(max_length=255, default="")
    raw_json = models.JSONField(default=dict)


class Key(models.Model):
    """
    License key model
    """

    key = models.CharField(max_length=255, default="")
    created_by = models.CharField(max_length=255, default="")
    created_at = models.BigIntegerField(default=0)
    create_reason = models.TextField(default="")
    redeemed_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )

class Transcript(models.Model):
    """
    Transcript model
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    html = models.TextField(default="")
    created_at = models.BigIntegerField(default=0)
    raw_json = models.JSONField(default=dict)
