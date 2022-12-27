"""
Admin API views
"""
import os

from django import http

from lightningbot import settings

from ..utils import keys, github, misc
from ..models import User, Key, Order, Release

# POST /api/v3/admin/create-key
def create_key(request: http.HttpRequest) -> http.HttpResponse:
    """
    Create a new API key for a user.
    """
    key = keys.create_key(
        create_reason="Admin Create Key", created_by=request.user.username
    )

    return http.JsonResponse({"error": False, "key": key.key})


# POST /api/v3/admin/create-release
def create_release(request: http.HttpRequest) -> http.HttpResponse:
    """
    Create a new release
    """
    version = request.POST.get("version")
    branch = request.POST.get("branch")
    changelog = request.POST.get("changelog")

    # save the executables from GitHub actions to static folder
    executables_path = os.path.join(settings.STATIC_ROOT, "executables")
    if not os.path.exists(executables_path):
        os.makedirs(executables_path)

    repo_name = ""

    if branch == "selfbot":
        repo_name = "LB-Selfbot"
    elif branch == "ui":
        repo_name = "LB-UI"

    try:
        github.download_latest_artifact("LightningDev1", repo_name, executables_path)
    except Exception as exc:
        return http.JsonResponse(
            {"error": True, "message": f"Failed to download artifact: {exc}"},
            status=500,
        )

    Release.objects.create(
        version=version,
        branch=branch,
        changelog=changelog,
    )

    return http.JsonResponse({"error": False, "release": ""})


# POST /api/v3/admin/table-data/users
def table_data_users(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Get table data for users
    """
    users = []

    for user in User.objects.all():
        login_time = misc.seconds_to_readable_time(user.login_time)

        flags = []

        if user.is_active:
            flags.append("Active")

        if user.is_staff:
            flags.append("Staff")

        if user.is_tester:
            flags.append("Tester")

        if user.is_superuser:
            flags.append("Superuser")

        users.append(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "loginData": f"{user.logins} logins, logged in for {login_time}",
                "key": user.redeemed_key.key if user.redeemed_key else "None",
                "accountType": user.account_type,
                "flags": ", ".join(flags),
                "createdAt": user.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if user.created_at
                else "None",
            }
        )

    return http.JsonResponse({"error": False, "data": users})


# POST /api/v3/admin/table-data/keys
def table_data_keys(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Get table data for keys
    """
    key_data = []

    for key in Key.objects.all():
        key_data.append(
            {
                "id": key.id,
                "key": key.key,
                "createdBy": key.created_by,
                "createdAt": key.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if key.created_at
                else "None",
                "createReason": key.create_reason,
                "redeemedBy": key.redeemed_by.username if key.redeemed_by else "None",
            }
        )

    return http.JsonResponse({"error": False, "data": key_data})


# POST /api/v3/admin/table-data/orders
def table_data_orders(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Get table data for keys
    """
    order_data = []

    for order in Order.objects.all():
        order_data.append(
            {
                "id": order.id,
                "user": order.user.username if order.user else "None",
                "status": order.status,
                "orderId": order.order_id,
                "key": order.key,
                "createdAt": order.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if order.created_at
                else "None",
            }
        )

    return http.JsonResponse({"error": False, "data": order_data})


# POST /api/v3/admin/table-data/releases
def table_data_releases(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Get table data for keys
    """
    releases_data = []

    for release in Release.objects.all():
        releases_data.append(
            {
                "id": release.id,
                "branch": release.branch,
                "version": release.version,
                "changelog": release.changelog,
                "createdAt": release.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if release.created_at
                else "None",
            }
        )

    return http.JsonResponse({"error": False, "data": releases_data})
