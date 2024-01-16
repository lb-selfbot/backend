"""
Selfbot API views
"""
import os
import re
import time
import json
import base64
import asyncio
import hashlib

import requests
import pytesseract
from PIL import Image
from io import BytesIO
from django import http
from django_ratelimit.decorators import ratelimit


from api.utils import keys, releases, logs, validation, obfuscation, misc
from api.utils.encryption import Encryption
from api.models import User, CreditKey

encryption = Encryption("NH62@Yyy5#5hsE56@S9*g2NY#11N$gguODE40QZ67kav1BvUHe")


# POST /api/v3/selfbot/reset-hwid
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
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
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
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
    request.user.hosting_credit += 31 * 24 * 60  # 1 month
    request.user.save()

    logs.create_entry(
        log_type="key_redeem",
        user=request.user,
        info={"key": key.key},
    )

    return http.JsonResponse({"error": False})


# POST /api/v3/selfbot/redeem-credit-key
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def redeem_credit_key(request: http.HttpRequest) -> http.HttpResponse:
    """
    Redeem a credit key
    """
    key = keys.get_credit_key_if_unredeemed(request.POST["key"])
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
    
    if request.POST["key"] == "LB-DOWNTIME-16-01-2024":
        try:
            CreditKey.objects.get(create_reason="Downtime compensation", redeemed_by=request.user)
        except CreditKey.DoesNotExist:
            pass
        else:
            return http.JsonResponse({"error": True, "message": "You have already used this promotion."}, status=400)

        key = keys.create_credit_key(
            create_reason="Downtime compensation",
            created_by="API",
            credit_amount=31 * 24 * 60,
        )

    if key is None:
        return http.JsonResponse({"error": True, "message": "Invalid key."}, status=400)

    key.redeemed_by = request.user
    key.save()

    request.user.hosting_credit += key.credit_amount
    if key.is_lifetime:
        request.user.hosting_lifetime = True
    request.user.save()

    logs.create_entry(
        log_type="credit_key_redeem",
        user=request.user,
        info={"key": key.key, "credit_amount": key.credit_amount},
    )

    return http.JsonResponse({"error": False})


# POST /api/v3/selfbot/check-version
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
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


# POST /api/v3/selfbot/enable-hosting
@ratelimit(key="ip", rate="5/m", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def enable_hosting(request: http.HttpRequest) -> http.HttpResponse:
    user: User = request.user

    if user.redeemed_key is None:
        return http.JsonResponse(
            {"error": True, "reason": "You must have a license key to use hosting."},
            status=400,
        )

    user.is_hosting = True
    user.hosting_token = request.POST["token"]
    user.save()

    return http.JsonResponse({"error": False})


# POST /api/v3/selfbot/disable-hosting
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def disable_hosting(request: http.HttpRequest) -> http.HttpResponse:
    user: User = request.user

    if user.redeemed_key is None:
        return http.JsonResponse(
            {"error": True, "reason": "You must have a license key to use hosting."},
            status=400,
        )

    user.is_hosting = False
    user.hosting_token = ""
    user.save()

    return http.JsonResponse({"error": False})


# GET /api/v3/selfbot/hosting/list-files
@ratelimit(key="ip", rate="10/m", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def hosting_list_files(request: http.HttpRequest) -> http.HttpResponse:
    user: User = request.user

    if user.redeemed_key is None:
        return http.JsonResponse(
            {"error": True, "reason": "You must have a license key to use hosting."},
            status=400,
        )

    folder_name = (
        misc.clean_filename(request.user.username) + "-" + str(request.user.id)
    )

    folder = os.path.join("/hosting", folder_name, "LightningBot")

    if not os.path.exists(folder):
        return http.JsonResponse(
            {
                "error": True,
                "reason": "You must enable hosting at least once before you can list files.",
            },
            status=400,
        )

    content = {}

    for root, subdirs, files in os.walk(folder):
        root = root.replace(folder, "/").replace("\\", "/").replace("//", "/")
        content[root] = {}

        content[root]["folders"] = subdirs.copy()
        content[root]["files"] = files.copy()

    return http.JsonResponse({"error": False, "content": content})


# POST /api/v3/selfbot/hosting/delete-folder
@ratelimit(key="ip", rate="5/m", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def hosting_delete_folder(request: http.HttpRequest) -> http.HttpResponse:
    user: User = request.user

    if user.redeemed_key is None:
        return http.JsonResponse(
            {"error": True, "reason": "You must have a license key to use hosting."},
            status=400,
        )

    folder_name = (
        misc.clean_filename(request.user.username) + "-" + str(request.user.id)
    )

    folder = os.path.join("/hosting", folder_name, "LightningBot")

    if not os.path.exists(folder):
        return http.JsonResponse(
            {
                "error": True,
                "reason": "You must enable hosting at least once before you can delete files.",
            },
            status=400,
        )

    folder_path = misc.clean_filename(request.POST["folder_path"], is_folder=True)

    while folder_path.startswith("/"):
        folder_path = folder_path[1:]

    requested_path = os.path.join(folder, folder_path)

    if os.path.commonprefix((os.path.realpath(requested_path), folder)) != folder:
        return http.JsonResponse(
            {"error": True, "reason": "Invalid folder path."}, status=400
        )

    if not os.path.exists(requested_path):
        return http.JsonResponse(
            {"error": True, "reason": "Folder does not exist."}, status=400
        )

    if len(os.listdir(requested_path)) != 0:
        return http.JsonResponse(
            {"error": True, "reason": "Folder is not empty."}, status=400
        )

    os.rmdir(requested_path)

    return http.JsonResponse({"error": False})


# GET /api/v3/selfbot/hosting/download-file
@ratelimit(key="ip", rate="5/m", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def hosting_download_file(request: http.HttpRequest) -> http.HttpResponse:
    user: User = request.user

    if user.redeemed_key is None:
        return http.JsonResponse(
            {"error": True, "reason": "You must have a license key to use hosting."},
            status=400,
        )

    folder_name = (
        misc.clean_filename(request.user.username) + "-" + str(request.user.id)
    )

    folder = os.path.join("/hosting", folder_name, "LightningBot")

    if not os.path.exists(folder):
        return http.JsonResponse(
            {
                "error": True,
                "reason": "You must enable hosting at least once before you can download files.",
            },
            status=400,
        )

    file_path = misc.clean_filename(request.GET.get("file_path", ""), is_folder=True)
    if file_path == "":
        return http.JsonResponse(
            {"error": True, "reason": "Missing file path."}, status=400
        )

    while file_path.startswith("/"):
        file_path = file_path[1:]

    requested_path = os.path.join(folder, file_path)

    if os.path.commonprefix((os.path.realpath(requested_path), folder)) != folder:
        return http.JsonResponse(
            {"error": True, "reason": "Invalid file path."}, status=400
        )

    if not os.path.exists(os.path.join(folder, file_path)):
        return http.JsonResponse(
            {"error": True, "reason": "File does not exist."}, status=400
        )

    with open(os.path.join(folder, file_path), "rb") as f:
        return http.HttpResponse(
            f.read(),
            content_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={file_path.split('/')[-1]}"
            },
        )


# POST /api/v3/selfbot/hosting/delete-file
@ratelimit(key="ip", rate="5/m", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def hosting_delete_file(request: http.HttpRequest) -> http.HttpResponse:
    user: User = request.user

    if user.redeemed_key is None:
        return http.JsonResponse(
            {"error": True, "reason": "You must have a license key to use hosting."},
            status=400,
        )

    folder_name = (
        misc.clean_filename(request.user.username) + "-" + str(request.user.id)
    )

    folder = os.path.join("/hosting", folder_name, "LightningBot")

    if not os.path.exists(folder):
        return http.JsonResponse(
            {
                "error": True,
                "reason": "You must enable hosting at least once before you can delete files.",
            },
            status=400,
        )

    file_path = misc.clean_filename(request.POST["file_path"], is_folder=True)

    while file_path.startswith("/"):
        file_path = file_path[1:]

    requested_path = os.path.join(folder, file_path)

    if os.path.commonprefix((os.path.realpath(requested_path), folder)) != folder:
        return http.JsonResponse(
            {"error": True, "reason": "Invalid file path."}, status=400
        )

    if not os.path.exists(requested_path):
        return http.JsonResponse(
            {"error": True, "reason": "File does not exist."}, status=400
        )

    os.remove(requested_path)

    return http.JsonResponse({"error": False})


# POST /api/v3/selfbot/start-params
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
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
@ratelimit(key="ip", rate="5/m", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
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


# POST /api/v3/selfbot/ocr
@ratelimit(key="ip", rate="5/m", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
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

        image = Image.open(BytesIO(image))

        extracted_text = pytesseract.image_to_string(image)

        return http.JsonResponse({"error": False, "text": extracted_text})
    except Exception as e:
        return http.JsonResponse({"error": True, "reason": str(e)}, status=500)


# POST /api/v3/selfbot/obfuscate
@ratelimit(key="ip", rate="5/m", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def obfuscate(request: http.HttpRequest) -> http.HttpResponse:
    """
    Obfuscate code
    """
    try:
        language = str(request.POST["lang"]).lower()
        code = str(request.POST["code"])

        match language:
            case "python":
                code = obfuscation.obfuscate_python(code)
            case "lua":
                code = obfuscation.obfuscate_lua(code)
            case "javascript":
                code = obfuscation.obfuscate_javascript(code)
            case _:
                return http.JsonResponse(
                    {"error": True, "reason": "Invalid language"}, status=400
                )

        return http.JsonResponse({"error": False, "code": code})
    except Exception as e:
        return http.JsonResponse({"error": True, "reason": str(e)}, status=500)
