"""
Admin API views
"""
import os

from django import http

from lightningbot import settings

from ..utils import keys, github, misc, password_reset
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

    if not request.user.is_superuser:
        return http.JsonResponse({"error": True, "message": "Not authorized"}, status=403)

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


# POST /api/v3/admin/delete-release
def delete_release(request: http.HttpRequest) -> http.HttpResponse:
    """
    Delete a release
    """
    release_id = request.POST.get("release_id")

    if not request.user.is_superuser:
        return http.JsonResponse({"error": True, "message": "Not authorized"}, status=403)
    
    try:
        release = Release.objects.get(id=release_id)
    except Release.DoesNotExist:
        return http.JsonResponse(
            {"error": True, "message": "Release does not exist"}, status=404
        )

    release.delete()

    return http.JsonResponse({"error": False})


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
                "email": user.email or "None",
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
                "rawJson": order.raw_json,
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


# POST /api/v3/admin/action/user
def action_user(request: http.HttpRequest) -> http.HttpResponse:
    """
    User actions
    """
    action: str = request.POST.get("action")
    user_id: int = request.POST.get("user_id")
    data = request.POST.get("data")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return http.JsonResponse(
            {"error": True, "message": "User does not exist!"}, status=404
        )
    
    if user.is_staff and not request.user.is_superuser:
        return http.JsonResponse(
            {"error": True, "message": "You cannot modify staff members!"}, status=403
        )

    match action:
        case "set_username":
            user.username = data
        case "set_password":
            user.set_password(data)
        case "set_email":
            user.email = data
        case "set_key":
            if data == "":
                user.redeemed_key = None
            else:
                try:
                    key = Key.objects.get(key=data)
                except Key.DoesNotExist:
                    return http.JsonResponse(
                        {"error": True, "message": "Key does not exist!"}, status=404
                    )

                user.redeemed_key = key
        case "set_active":
            user.is_active = data == "true"
        case "set_staff":
            user.is_staff = data == "true"
        case "set_tester":
            user.is_tester = data == "true"
        case "delete":
            user.delete()
        case "reset_free_trial":
            user.free_trial_expiry = 0
        case "send_password_reset_email":
            password_reset.send_reset_password_email(request, user)

    if action != "delete":
        user.save()

    return http.JsonResponse({"error": False})


# POST /api/v3/admin/action/key
def action_key(request: http.HttpRequest) -> http.HttpResponse:
    """
    Key actions
    """
    action: str = request.POST.get("action")
    key_id: int = request.POST.get("key_id")

    try:
        key = Key.objects.get(id=key_id)
    except Key.DoesNotExist:
        return http.JsonResponse(
            {"error": True, "message": "Key does not exist!"}, status=404
        )

    match action:
        case "delete":
            key.delete()
        case "set_unredeemed":
            if key.redeemed_by:
                key.redeemed_by.redeemed_key = None
                key.redeemed_by.account_type = "None"
                key.redeemed_by.save()

            key.redeemed_by = None
            key.save()

    return http.JsonResponse({"error": False})
