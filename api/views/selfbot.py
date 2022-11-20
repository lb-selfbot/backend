"""
Selfbot API views
"""
import time
from django import http
from api.utils import keys

# POST /api/v3/selfbot/reset_hwid
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
    return http.JsonResponse({"status": 200})


# POST /api/v3/selfbot/redeem_key
def redeem_key(request: http.HttpRequest) -> http.HttpResponse:
    """
    Redeem a license key
    """
    key = keys.is_key_valid(request.POST["key"])
    if key is None:
        return http.JsonResponse({"status": 400, "message": "Invalid key."}, status=400)
    key.redeemed_by = request.user
    request.user.redeemed_key = key
    request.user.account_type = "Lifetime"
    key.save()
    request.user.save()
    return http.JsonResponse({"status": 200})
