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
    last_selfbot_ping = models.DateTimeField(blank=True, null=True)
    logins = models.IntegerField(default=0)
    heartbeats = models.IntegerField(default=0)
    login_time = models.BigIntegerField(default=0)
    hwid = models.CharField(max_length=255, default="")
    hwid_resets = models.JSONField(default=list)
    redeemed_key = models.ForeignKey(
        "Key", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Hosting
    is_hosting = models.BooleanField(default=False)
    hosting_credit = models.IntegerField(default=0)  # In minutes
    hosting_lifetime = models.BooleanField(default=False)
    hosting_token = models.CharField(max_length=512, default="")  # RSA encrypted token


class PasswordResetToken(models.Model):
    """
    Password reset token model
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.BigIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.token}"


class Order(models.Model):
    """
    Order model
    """

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=64, default="")
    order_id = models.CharField(max_length=255, default="")
    key = models.CharField(max_length=255, default="")
    raw_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.order_id} - {self.status}"


class Key(models.Model):
    """
    License key model
    """

    key = models.CharField(max_length=255, default="")
    created_by = models.CharField(max_length=255, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    create_reason = models.TextField(default="")
    redeemed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.key} - {self.redeemed_by.username if self.redeemed_by else 'Unredeemed'}"


class CreditKey(models.Model):
    """
    Credit key model
    """

    key = models.CharField(max_length=255, default="")
    created_by = models.CharField(max_length=255, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    create_reason = models.TextField(default="")
    credit_amount = models.IntegerField(default=0)
    is_lifetime = models.BooleanField(default=False)
    redeemed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.key} - {self.credit_amount // (24 * 60)} days - {self.redeemed_by.username if self.redeemed_by else 'Unredeemed'}"


class Transcript(models.Model):
    """
    Transcript model
    """

    html = models.TextField(default="")
    code = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.code


class Release(models.Model):
    """
    Release model
    """

    version = models.CharField(max_length=255, default="")
    branch = models.CharField(max_length=255, default="")
    changelog = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.version} - {self.branch}"


class Log(models.Model):
    """
    Log model
    """

    log_type = models.CharField(max_length=255, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    info = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.log_type} - {self.user.username if self.user else 'No user'}"


class Image(models.Model):
    """
    Image model for imagegen
    """

    image = models.BinaryField()
    format = models.CharField(max_length=16, default="")
    name = models.CharField(max_length=255, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.format} - {self.created_at}"
