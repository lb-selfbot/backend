"""
ASGI config for lightningbot project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

from clyde_bot.bot import run_clyde_bot

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lightningbot.settings")

import api.urls

run_clyde_bot()

django_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_app,
        "websocket": AllowedHostsOriginValidator(
            SessionMiddlewareStack(
                AuthMiddlewareStack(URLRouter(api.urls.websocket_urlpatterns))
            )
        ),
    }
)
