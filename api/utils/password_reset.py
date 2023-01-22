"""
Password reset utils
"""
import time
from django import http
from django.core import mail
from django.template import loader

import user_agents
import requests

from lightningbot import settings

from ..models import User, PasswordResetToken
from ..utils import misc, logs


def create_password_reset_token(user: User) -> PasswordResetToken:
    """
    Create a password reset token for a user
    """
    # Delete any existing tokens for this user
    PasswordResetToken.objects.filter(user=user).delete()

    return PasswordResetToken.objects.create(
        user=user,
        token=misc.random_string(32),
        created_at=round(time.time()),
    )


def check_password_reset_token(user: User, token: PasswordResetToken) -> bool:
    """
    Check if a password reset token is valid
    """
    try:
        token = PasswordResetToken.objects.filter(token=token).get(user=user)
    except PasswordResetToken.DoesNotExist:
        return False

    # If we are here, either the token is valid or has expired
    # so it's safe to delete it
    token.delete()

    # Check if the token was created within the last 24 hours
    return time.time() - token.created_at < 86400


def send_reset_password_email(request: http.HttpRequest, user: User) -> bool:
    """
    Send a password reset token to a user
    """

    if user.email == "":
        return False

    # Parse the user agent so we can get OS, browser, etc.
    user_agent = user_agents.parse(request.headers.get("User-Agent"))

    token = create_password_reset_token(user)

    action_url = (
        "https://lightning-bot.com/forgot-password"
        + f"?username={user.username}&token={token.token}"
    )

    # Load email template from emails/password_reset.html
    email_html = loader.render_to_string(
        "email/password_reset.html",
        {
            "name": user.username,
            "action_url": action_url,
            "operating_system": user_agent.get_os(),
            "browser_name": user_agent.browser.family,
            "support_url": "mailto:support@lightning-bot.com",
        },
    )

    json_data = {
        "personalizations": [
            {
                "to": [{"email": user.email, "name": user.username}],
            }
        ],
        "from": {
            "email": "lightning@lightning-bot.com",
            "name": "LightningBot",
        },
        "subject": "LightningBot - Password Reset",
        "content": [{"type": "text/html", "value": email_html}],
    }

    response = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={
            "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
            "Content-Type": "application/json",
        },
        json=json_data,
    )

    print(response.status_code, response.text)

    logs.create_entry(log_type="send_reset_password_email", user=user, info={})

    return True
