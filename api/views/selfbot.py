"""
Selfbot API views
"""
import time
import base64
import hashlib

from django import http

from api.utils import keys, releases, logs, validation
from api.utils.encryption import Encryption

encryption = Encryption("NH62@Yyy5#5hsE56@S9*g2NY#11N$gguODE40QZ67kav1BvUHe")


# POST /api/v3/selfbot/reset-hwid
def reset_hwid(request: http.HttpRequest) -> http.HttpResponse:
    """
    Reset HWID
    """
    if request.user.hwid == "":
        return http.JsonResponse(
            {
                "status": 400,
                "message": "You already have no HWID set.",
            },
            status=400,
        )

    request.user.hwid = ""
    request.user.hwid_resets.append(time.time())

    request.user.save()

    logs.create_entry(
        log_type="hwid_reset",
        user=request.user,
        info={},
    )

    return http.JsonResponse({"error": False})


# POST /api/v3/selfbot/redeem-key
def redeem_key(request: http.HttpRequest) -> http.HttpResponse:
    """
    Redeem a license key
    """
    key = keys.get_key_if_unredeemed(request.POST["key"])
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

    if key is None:
        return http.JsonResponse({"error": True, "message": "Invalid key."}, status=400)

    key.redeemed_by = request.user
    key.save()

    request.user.redeemed_key = key
    request.user.account_type = "Premium"
    request.user.save()

    logs.create_entry(
        log_type="key_redeem",
        user=request.user,
        info={"key": key.key},
    )

    return http.JsonResponse({"error": False})


# POST /api/v3/selfbot/check-version
def check_version(request: http.HttpRequest) -> http.HttpResponse:
    """
    Check the latest version of the bot
    """
    branch = request.POST["branch"]
    version = request.POST["version"]

    latest_release = releases.get_latest(branch)
    if latest_release is None:
        return http.JsonResponse(
            {"error": True, "reason": "Invalid branch"}, status=400
        )

    is_latest = latest_release.version == version

    return http.JsonResponse(
        {
            "error": False,
            "is_latest": is_latest,
            "latest": {
                "version": latest_release.version,
                "branch": latest_release.branch,
                "changelog": latest_release.changelog,
            },
        }
    )


# POST /api/v3/selfbot/start-params
def start_params(request: http.HttpRequest) -> http.HttpResponse:
    """
    Check start params
    """

    data = {
        "status": "ok",
    }

    encrypted = encryption.encrypt(data)

    hashed: bytes = hashlib.sha512(encrypted.encode("ascii")).digest()

    new_hash = bytearray()

    for i, hash_byte in enumerate(hashed):
        if i % 2 == 0:
            continue

        new_hash.append(hash_byte ^ i)

    return http.HttpResponse(
        encrypted,
        content_type="application/octet-stream",
        headers={
            "cf-ray-id": base64.b64encode(new_hash).decode("ascii"),
        },
    )
