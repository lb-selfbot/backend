"""
Selfbot API views
"""
import time
from django import http
from api.utils import keys, releases

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
    return http.JsonResponse({"error": False})


# POST /api/v3/selfbot/redeem-key
def redeem_key(request: http.HttpRequest) -> http.HttpResponse:
    """
    Redeem a license key
    """
    key = keys.is_key_valid(request.POST["key"])
    if key is None:
        return http.JsonResponse({"error": True, "message": "Invalid key."}, status=400)
    key.redeemed_by = request.user
    request.user.redeemed_key = key
    request.user.account_type = "Lifetime"
    key.save()
    request.user.save()
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
        return http.JsonResponse({"error": True, "reason": "Invalid branch"}, status=400)

    is_latest = latest_release.version == version

    return http.JsonResponse(
        {
            "error": False,
            "is_latest": is_latest,
            "latest": {
                "version": latest_release.version,
                "branch": latest_release.branch,
                "changelog": latest_release.changelog,
                "filename": latest_release.filename,
            },
        }
    )
