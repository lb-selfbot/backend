"""
Validation functions for the API.
"""
import os
import re

from django import http
import requests

from api.models import User
from .misc import get_user_ip
import logs


class ValidationResult:
    """
    Validation results
    """

    MissingField = 0xAFE3E
    UsernameLength = 0xCD9A6
    PasswordLength = 0xDB8EA
    UsernameInvalid = 0xAFE3F
    UsernameTaken = 0xAB2F3
    Success = 0

    def __index__(self) -> int:
        return int(self)

    @staticmethod
    def to_string(validation_result: "ValidationResult") -> str:
        """
        Convert a validation error to a string
        """
        return hex(validation_result)[2:].upper()


def validate_captcha(request: http.HttpRequest, captcha_response: str) -> bool:
    """
    Validate a reCAPTCHA response
    """
    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={
            "secret": os.environ["RECAPTCHA_SECRET_KEY"],
            "response": captcha_response,
            "remoteip": get_user_ip(request),
        },
        timeout=5,
    )

    json = response.json()

    accepted = json["success"] and json["score"] >= 0.4

    logs.create_entry(
        log_type="captcha_validation",
        user=request.user,
        info={
            "result": json,
            "accepted": accepted,
            "url": request.build_absolute_uri(),
        },
    )

    return accepted


def validate_user(username: str, password: str) -> ValidationResult:
    """
    Validate a username and password
    """
    # Check if username and password aren"t empty
    if not username or not password:
        return ValidationResult.MissingField
    # Check if username has more than 3 and less than 40 characters
    if len(username) < 3 or len(username) > 40:
        return ValidationResult.UsernameLength
    # Check if password has at least 6 characters
    if len(password) < 6:
        return ValidationResult.PasswordLength
    if not re.match(r"^[a-zA-Z0-9_.]+$", username):
        return ValidationResult.UsernameInvalid
    if User.objects.filter(username=username).exists():
        return ValidationResult.UsernameTaken
    return ValidationResult.Success
