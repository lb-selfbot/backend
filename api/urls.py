"""
Django URLs
"""
from django.urls import re_path

from . import websocket_consumers
from . import routes


urlpatterns = [route.get_path() for route in routes.routes]

websocket_urlpatterns = [
    re_path("api/v3/ws/selfbot", websocket_consumers.selfbot.SelfbotConsumer.as_asgi()),
    re_path("api/v3/ws/website", websocket_consumers.website.WebsiteConsumer.as_asgi()),
]
