"""
Website websocket consumer
"""

import json
import typing
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.auth import get_user

from ..models import User


class WebsiteConsumer(WebsocketConsumer):
    """
    Websocket consumer for the website
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.django_user: User = None
        self.group_name: str = None

    def group_add(self, group_name: str, channel_name: str):
        """
        Sync version of self.channel_layer.group_add
        """
        return async_to_sync(self.channel_layer.group_add)(group_name, channel_name)

    def group_send(self, group_name: str, message: typing.Dict[str, any]):
        """
        Sync version of self.channel_layer.group_send
        """
        return async_to_sync(self.channel_layer.group_send)(group_name, message)

    def group_discard(self, group_name: str, channel_name: str):
        """
        Sync version of self.channel_layer.group_discard
        """
        return async_to_sync(self.channel_layer.group_discard)(group_name, channel_name)

    def send_to_website(self, message: typing.Dict[str, any], close: bool = False):
        """
        Send a message to the website websocket
        """
        self.send(json.dumps(message), close=close)

    def close_ws(self, code: int):
        """
        Close the websocket
        """
        if self.group_name:
            self.group_discard(self.group_name, self.channel_name)
        self.close(code)

    def connect(self):
        """
        Called when a WebSocket connection is opened.
        """
        self.django_user = self.scope["user"]

        self.group_name = f"websocket_user_{self.django_user.id}"

        # Make sure the user is authenticated
        if self.django_user is None or not self.django_user.is_authenticated:
            self.close()
            return

        self.accept()

        # Add this channel to the user's channel group
        self.group_add(self.group_name, self.channel_name)

        self.group_send(
            self.group_name,
            {
                "type": "website_connect",
                "channel": self.channel_name,
            },
        )

    def disconnect(self, code):
        """
        Called when a WebSocket connection is closed.
        """
        if self.group_name:
            self.group_discard(self.group_name, self.channel_name)

    def receive(self, text_data: str = None, bytes_data: bytes = None):
        """
        Called when a WebSocket message is received
        """
        # Try to parse the message as JSON
        try:
            message = json.loads(text_data)
        except ValueError:
            self.close_ws(3003)
            return

        # Relay message to the selfbot
        relay_ops = ["EXIT", "RESTART", "CONFIG_UPDATE"]
        if message.get("op") in relay_ops:
            self.group_send(
                self.group_name,
                {
                    "type": "website_to_selfbot_relay",
                    "data": message,
                },
            )
        elif message.get("op") == "PING":
            self.send_to_website({"op": "PONG"})

    def selfbot_connect(self, event):
        """
        Called when the selfbot websocket is connected
        """
        self.send_to_website(
            {
                "op": "SELFBOT_CONNECT",
                "data": {
                    "computer_name": event.get("computer_name"),
                    "console_text": event.get("console_text"),
                },
            }
        )

    def selfbot_disconnect(self, _event):
        """
        Called when the selfbot websocket is disconnected
        """
        self.send_to_website(
            {
                "op": "SELFBOT_DISCONNECT",
            }
        )

    def website_connect(self, _event):
        """
        Called when the website websocket is connected
        This is a no-op because we sent the message ourselves
        """

    def selfbot_to_website_relay(self, event):
        """
        Called when a message is relayed from the selfbot websocket to the website websocket
        """
        self.send_to_website(event.get("data"))

    def website_to_selfbot_relay(self, _event):
        """
        Called when a message is relayed from the website websocket to the selfbot websocket
        This is a no-op because we sent the message ourselves
        """
