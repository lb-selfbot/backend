"""
API views for the Discord bot
"""
from django import http

from ..models import Transcript
from ..utils import keys, misc


def create_key(request: http.HttpRequest) -> http.JsonResponse:
    """
    Create a new license key
    """
    created_by = request.POST["created_by"]
    key = keys.create_key(create_reason="Discord Bot", created_by=created_by)

    return http.JsonResponse({"error": False, "key": key.key})


def check_key(request: http.HttpRequest) -> http.JsonResponse:
    """
    Check if a key is valid
    """
    key = request.GET.get("key")
    if key is None:
        return http.JsonResponse({"error": True, "rason": "Missing key"}, status=400)

    key = keys.get_key_if_unredeemed(key)
    if key is None:
        return http.JsonResponse(
            {"error": True, "reason": "That key is invalid!"}, status=400
        )

    redeemed_by = {
        "username": "Key is not redeemed",
        "id": "",
    }

    if key.redeemed_by is not None:
        redeemed_by = {
            "username": key.redeemed_by.username,
            "id": str(key.redeemed_by.id),
        }

    return http.JsonResponse(
        {
            "error": False,
            "key": {
                "key": key.key,
                "created_by": key.created_by,
                "created_at": misc.format_datetime(key.created_at),
                "create_reason": key.create_reason,
                "redeemed_by": redeemed_by,
            },
        }
    )

def create_transcript(request: http.HttpRequest) -> http.JsonResponse:
    """
    Create a transcript
    """
    html = request.POST["html"]
    if html is None:
        return http.JsonResponse({"error": True, "reason": "Missing html"}, status=400)

    code = misc.random_string(15)

    Transcript.objects.create(html=html, code=code)

    return http.JsonResponse({"error": False, "code": code})
