"""
Selfbot websocket consumer
"""

import os
import time
import typing
import random
import string

from django.utils import timezone
from django.contrib import auth
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from ..utils.encryption import Encryption

from ..models import User

encryption = Encryption(os.environ["ENCRYPTION_KEY"])


class SelfbotConsumer(WebsocketConsumer):
    """
    Websocket consumer for the website
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.django_user: User = None
        self.group_name: str = None

        self.username: str = None
        self.password: str = None
        self.computer_name: str = None
        self.console_text: str = None

        self.instance_id = random.choices(string.ascii_letters + string.digits, k=50)

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

    def send_to_selfbot(self, message: typing.Dict[str, any], close: bool = False):
        """
        Send a message to the selfbot websocket
        """
        self.send(encryption.encrypt(message), close=close)

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
        self.accept()

    def disconnect(self, code):
        """
        Called when a WebSocket connection is closed.
        """
        if self.group_name:
            self.group_send(
                self.group_name,
                {"type": "selfbot_disconnect", "channel": self.channel_name},
            )
            self.group_discard(self.group_name, self.channel_name)

    def login(self):
        """
        Try to log the selfbot in
        """
        if self.django_user is None:
            return 3010

        if not self.django_user.is_active or not self.django_user.is_authenticated:
            # User is not active or not authenticated, close connection
            return 3010

        if self.django_user.redeemed_key is None:
            # User has not redeemed a key, check for free trial
            if self.django_user.free_trial_expiry == 0:
                # Start free trial (7 days)
                self.django_user.free_trial_expiry = int(time.time()) + 86400 * 7
                self.django_user.account_type = "Free Trial"
                self.send_to_selfbot({"op": "FREE_TRIAL_START"})
            elif self.django_user.free_trial_expiry < int(time.time()):
                # Free trial expired, close connection
                return 3011

        self.django_user.last_login = timezone.now()
        self.django_user.logins = self.django_user.logins + 1
        self.django_user.save()
        return 0

    def receive(
        self, text_data: typing.Dict[any, any] = None, bytes_data: bytes = None
    ):
        """
        Called when a WebSocket message is received
        """
        try:
            json_message = encryption.decrypt(text_data)
        except (IndexError, ValueError, UnicodeError):
            self.close(3003)
        else:
            return self.receive_json(json_message)
        return None

    def receive_json(self, json_message: typing.Dict[any, any]):
        """
        Called when a WebSocket JSON message is received
        """
        json_data = json_message.get("data", {})
        match json_message.get("op"):
            case "HELLO":
                self.username = json_data.get("username", "")
                self.password = json_data.get("password", "")

                self.computer_name = json_data.get("computer_name", "")
                self.console_text = json_data.get("console_text", "")

                user: User = auth.authenticate(
                    username=self.username, password=self.password
                )

                if user is None:
                    self.close_ws(3004)
                    return

                self.django_user = user
                self.group_name = f"websocket_user_{self.django_user.id}"

                # Close websocket if the user is not allowed to login
                if (code := self.login()) != 0:
                    self.close_ws(code)
                    return

                self.group_add(self.group_name, self.channel_name)

                self.group_send(
                    self.group_name,
                    {
                        "type": "selfbot_connect",
                        "channel_name": self.channel_name,
                        "computer_name": self.computer_name,
                    },
                )

                self.send_to_selfbot({"op": "HELLO_ACK"})
            case "PING":
                # Add 1 minute to login time
                self.django_user.login_time += 60
                self.django_user.save()
                self.send_to_selfbot({"op": "PONG"})
            case "CONSOLE_APPEND" | "CONSOLE_CLEAR" | "CONSOLE_SET" | "CONFIG_UPDATE":
                # Generic case to relay message to website
                self.group_send(
                    self.group_name,
                    {
                        "type": "selfbot_to_website_relay",
                        "data": json_message,
                    },
                )

    def selfbot_connect(self, event):
        """
        Called when the selfbot websocket is connected
        """

        if event.get("channel_name") != self.channel_name:
            print("ANOTHER_SELFBOT_CONNECTED")
            self.send_to_selfbot(
                {
                    "op": "ANOTHER_SELFBOT_CONNECTED",
                    "data": {
                        "computer_name": event.get("computer_name"),
                    },
                },
                close=3006,
            )

    def selfbot_disconnect(self, _event):
        """
        Called when the selfbot websocket is disconnected
        This is a no-op because we sent the message ourselves
        """

    def website_connect(self, _event):
        """
        Called when the website websocket is connected
        """
        self.group_send(
            self.group_name,
            {
                "type": "selfbot_connect",
                "channel_name": self.channel_name,
                "computer_name": self.computer_name,
                "console_text": self.console_text,
            },
        )
        self.send_to_selfbot({"op": "WEBSITE_CONNECT"})

    def selfbot_to_website_relay(self, _event):
        """
        Called when a message is relayed from the selfbot websocket to the website websocket
        This is a no-op because we sent the message ourselves
        """

    def website_to_selfbot_relay(self, event):
        """
        Called when a message is relayed from the website websocket to the selfbot websocket
        """
        self.send_to_selfbot(event.get("data"))
