"""
Selfbot API views
"""
import time
import json
import base64
import asyncio
import hashlib

import requests
import pytesseract
from django import http
from PIL import Image

from api.utils import keys, releases, logs, validation
from api.utils.encryption import Encryption
from clyde_bot.bot import ClydeJob, clyde_bot

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
def start_params(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Check start params
    """

    data = {
        "status": "ok",
    }

    data_string = json.dumps(data)

    encrypted = encryption.encrypt(data_string)

    hashed: bytes = hashlib.sha512(data_string.encode("ascii")).digest()

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


discord_headers = {
    "accept": "*/*",
    "accept-language": "en-US,nl-NL;q=0.9",
    "authorization": "Bot MTA0MTMwMjcxMTc1MDExOTUwNA.G9V-JK.2-r-eEJZqZeFBV6WcTHAGNop71y9v2kDrpOyJk",
    "content-type": "application/json",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-debug-options": "bugReporterEnabled",
    "x-discord-locale": "en-US",
}


# POST /api/v3/selfbot/gen-image-key
def gen_image_key(request: http.HttpRequest) -> http.HttpResponse:
    """
    Generate an image key
    """
    image_url = request.POST["image_url"]

    try:
        response = requests.post(
            "https://discord.com/api/v9/channels/1070776322449748129/messages",
            json={
                "embeds": [
                    {
                        "type": "rich",
                        "description": "",
                        "thumbnail": {"url": image_url},
                    },
                ],
                "tts": False,
            },
            headers=discord_headers,
            timeout=10,
        )
    except requests.exceptions.RequestException:
        return http.JsonResponse(
            {"error": True, "reason": "Failed to connect to Discord"}, status=500
        )

    if response.status_code != 200:
        return http.JsonResponse(
            {"error": True, "reason": "Failed to connect to Discord"}, status=500
        )

    try:
        proxy_url = str(response.json()["embeds"][0]["thumbnail"]["proxy_url"])
    except KeyError:
        return http.JsonResponse(
            {"error": True, "reason": "Failed to connect to Discord"}, status=500
        )

    image_key = "mp:external/" + proxy_url.split("external/")[-1]

    return http.JsonResponse({"error": False, "image_key": image_key})


# POST /api/v3/selfbot/clyde
def clyde(request: http.HttpRequest) -> http.HttpResponse:
    """
    Generate a Clyde (OpenAI) response
    """
    try:
        message = request.POST["message"]

        job = ClydeJob(request.user.username, message)

        clyde_bot.tasks.sync_q.put(job)

        response, error = clyde_bot.wait_for_response(job)

        if error:
            return http.JsonResponse({"error": True, "reason": response}, status=500)

        return http.JsonResponse({"error": False, "response": response})
    except Exception as e:
        return http.JsonResponse({"error": True, "reason": str(e)}, status=500)


# POST /api/v3/selfbot/ocr
def ocr(request: http.HttpRequest) -> http.HttpResponse:
    """
    Extract text from an image
    """
    try:
        image_link = request.POST["image"]

        # validate image
        if not image_link.startswith("http"):
            return http.JsonResponse(
                {"error": True, "reason": "Invalid image link"}, status=400
            )
        
        if not image_link.endswith((".png", ".jpg", ".jpeg", ".gif")):
            return http.JsonResponse(
                {"error": True, "reason": "Invalid image link"}, status=400
            )
        
        image = requests.get(image_link, timeout=5).content

        image = Image.open(image)

        extracted_text = pytesseract.image_to_string(image)

        return http.JsonResponse({"error": False, "text": extracted_text})
    except Exception as e:
        return http.JsonResponse({"error": True, "reason": str(e)}, status=500)
