"""
ASGI config for lightningbot project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lightningbot.settings")

django_app = get_asgi_application()

import api.urls

application = ProtocolTypeRouter(
    {
        "http": django_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(api.urls.websocket_urlpatterns))
        ),
    }
)
