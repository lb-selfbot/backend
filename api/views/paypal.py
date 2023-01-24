"""
PayPal API views
"""
from django import http

from paypalhttp import HttpError

from api.utils.paypal_sdk import paypal_sdk
from api.utils import validation


# GET /api/v3/paypal/create_order
def create_order(request: http.HttpRequest) -> http.HttpResponse:
    """
    Create a PayPal order
    """
    captcha_token: str = request.POST["captcha_token"]

    if not validation.validate_captcha(request, captcha_token):
        return http.JsonResponse(
            {
                "status": 400,
                "error": "INVALID_CAPTCHA",
                "message": "Invalid captcha response.",
            },
            status=400,
        )

    try:
        order_id = paypal_sdk.create_order()
    except HttpError as http_error:
        return http.JsonResponse(
            {"status": 500, "message": http_error.message},
            status=500,
        )
    return http.JsonResponse({"status": 200, "order_id": order_id})


# POST /api/v3/paypal/capture_order
def capture_order(request: http.HttpRequest) -> http.HttpResponse:
    """
    Capture a PayPal order
    """
    order_id: str = request.POST["order_id"]
    try:
        data = paypal_sdk.capture_order(request.user, order_id)  # type: ignore
    except HttpError as http_error:
        return http.JsonResponse(
            {"status": 500, "message": http_error.message}, status=500
        )
    return http.JsonResponse({"status": 200, "data": data})
