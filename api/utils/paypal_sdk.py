"""
PayPal SDK utils
"""
import os
import json

from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest

from api.models import User, Order
from . import keys, logs


class PayPalSDK:
    """
    PayPal SDK class
    """

    def __init__(self):
        self.sandbox = os.environ.get("PAYPAL_SANDBOX") == "true"
        if self.sandbox:
            self.client_id = os.environ.get("PAYPAL_SANDBOX_CLIENT_ID")
            self.client_secret = os.environ.get("PAYPAL_SANDBOX_CLIENT_SECRET")
            self.environment = SandboxEnvironment(
                client_id=self.client_id, client_secret=self.client_secret
            )
        else:
            self.client_id = os.environ.get("PAYPAL_CLIENT_ID")
            self.client_secret = os.environ.get("PAYPAL_CLIENT_SECRET")
            self.environment = LiveEnvironment(
                client_id=self.client_id, client_secret=self.client_secret
            )

        self.client = PayPalHttpClient(self.environment)

    def create_order(self):
        """
        Create a PayPal order
        """
        request = OrdersCreateRequest()
        request.prefer("return=representation")
        request.request_body(
            {
                "intent": "CAPTURE",
                "application_context": {
                    "return_url": "https://lightning-bot.com/dashboard",
                    "cancel_url": "https://lightning-bot.com/dashboard",
                    "shipping_preference": "NO_SHIPPING",
                },
                "purchase_units": [
                    {
                        "description": "LightningBot",
                        "amount": {"currency_code": "EUR", "value": "5.00"},
                    }
                ],
            }
        )
        response = self.client.execute(request)

        logs.create_entry(
            log_type="paypal_order_created",
            user=None,
            info={"order_id": response.result.id, "sandbox": self.sandbox},
        )

        return response.result.id

    def capture_order(self, user: User, order_id: str):
        """
        Capture a PayPal order
        """
        request = OrdersCaptureRequest(order_id)
        response = self.client.execute(request)
        response.raw_result = response.result.dict()

        raw_json = json.dumps(response.raw_result, indent=4)
        key_instance = None

        if response.raw_result["status"] == "COMPLETED":
            user.email = response.raw_result["payer"]["email_address"]

            key_instance = keys.create_key(
                user=user, create_reason=f"Purchase ({order_id})", created_by="API"
            )

        response.raw_result["key"] = key_instance.key if key_instance else ""

        logs.create_entry(
            log_type="paypal_order_captured",
            user=user,
            info={
                "order_id": order_id,
                "status": response.raw_result["status"],
                "key": response.raw_result["key"],
                "raw_json": raw_json,
                "sandbox": self.sandbox,
            },
        )

        Order.objects.create(
            user=user,
            status=response.raw_result["status"],
            order_id=order_id,
            key=response.raw_result["key"],
            raw_json=raw_json,
        )

        return response.raw_result


paypal_sdk = PayPalSDK()
