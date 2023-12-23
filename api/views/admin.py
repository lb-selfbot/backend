"""
Admin API views
"""
import os

from django import http
from django.utils import timezone
from django_ratelimit.decorators import ratelimit

from lightningbot import settings

from ..utils import keys, github, misc, password_reset, logs
from ..models import User, CreditKey, Key, Order, Release


def get_flags(user: User) -> list[str]:
    flags = []

    if user.is_active:
        flags.append("Active")

    if user.is_staff:
        flags.append("Staff")

    if user.is_tester:
        flags.append("Tester")

    if user.is_superuser:
        flags.append("Superuser")

    if user.is_hosting:
        flags.append("Hosting")

    if user.hosting_lifetime:
        flags.append("Lifetime Hosting")

    return flags


# POST /api/v3/admin/create-key
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def create_key(request: http.HttpRequest) -> http.HttpResponse:
    """
    Create a new API key for a user.
    """
    key = keys.create_key(
        create_reason="Admin Create Key", created_by=request.user.username
    )

    return http.JsonResponse({"error": False, "key": key.key})


# POST /api/v3/admin/create-credit-key
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def create_credit_key(request: http.HttpRequest) -> http.HttpResponse:
    """
    Create a new API key for a user.
    """
    key = keys.create_credit_key(
        create_reason="Admin Create Key",
        created_by=request.user.username,
        credit_amount=int(request.POST["credit_amount"]),
        is_lifetime=request.POST["is_lifetime"] == "true",
    )

    return http.JsonResponse({"error": False, "key": key.key})


# POST /api/v3/admin/create-release
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def create_release(request: http.HttpRequest) -> http.HttpResponse:
    """
    Create a new release
    """
    version = request.POST.get("version")
    branch = request.POST.get("branch")
    changelog = request.POST.get("changelog")

    if not request.user.is_superuser:
        return http.JsonResponse(
            {"error": True, "message": "Not authorized"}, status=403
        )

    # Save the executables from GitHub actions to static folder
    executables_path = os.path.join(settings.STATIC_ROOT, "executables")
    if not os.path.exists(executables_path):
        os.makedirs(executables_path)

    repo_name = ""

    if branch == "selfbot":
        repo_name = "LB-Selfbot"
    elif branch == "ui":
        repo_name = "LB-UI"
    else:
        return http.JsonResponse(
            {"error": True, "message": "Invalid branch"},
            status=400,
        )

    try:
        github.download_latest_artifact("LightningDev1", repo_name, executables_path)
    except Exception as exc:
        return http.JsonResponse(
            {"error": True, "message": f"Failed to download artifact: {exc}"},
            status=500,
        )

    if branch == "selfbot" and os.path.isfile("/hosting/LB-Selfbot-New"):
        os.rename("/hosting/LB-Selfbot-New", "/hosting/LB-Selfbot")
        os.system("sudo systemctl restart lightningbot-hosting")

    logs.create_entry(
        log_type="create_release",
        user=request.user,
        info={
            "version": version,
            "branch": branch,
            "changelog": changelog,
        },
    )

    Release.objects.create(
        version=version,
        branch=branch,
        changelog=changelog,
    )

    return http.JsonResponse({"error": False, "release": ""})


# POST /api/v3/admin/delete-release
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def delete_release(request: http.HttpRequest) -> http.HttpResponse:
    """
    Delete a release
    """
    release_id = request.POST.get("release_id")

    if not request.user.is_superuser:
        return http.JsonResponse(
            {"error": True, "message": "Not authorized"}, status=403
        )

    try:
        release = Release.objects.get(id=release_id)
    except Release.DoesNotExist:
        return http.JsonResponse(
            {"error": True, "message": "Release does not exist"}, status=404
        )

    release.delete()

    logs.create_entry(
        log_type="delete_release",
        user=request.user,
        info={"release_id": release_id},
    )

    return http.JsonResponse({"error": False})


# POST /api/v3/admin/deploy-docs
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def deploy_docs(request: http.HttpRequest) -> http.HttpResponse:
    """
    Deploy docs
    """
    if not request.user.is_superuser:
        return http.JsonResponse(
            {"error": True, "message": "Not authorized"}, status=403
        )

    # Save the static site from GitHub actions to the docs folder
    docs_path = "/var/www/docs.lightning-bot.com"
    if not os.path.exists(docs_path):
        os.makedirs(docs_path)

    try:
        github.download_latest_artifact("LightningDev1", "LB-Docs", docs_path)
    except Exception as exc:
        return http.JsonResponse(
            {"error": True, "message": f"Failed to download artifact: {exc}"},
            status=500,
        )

    logs.create_entry(
        log_type="deploy_docs",
        user=request.user,
        info={},
    )

    return http.JsonResponse({"error": False})


# POST /api/v3/admin/provide-hosting-credit
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def provide_hosting_credit(request: http.HttpRequest) -> http.HttpResponse:
    """
    Provide Hosting Credit
    """
    if not request.user.is_superuser:
        return http.JsonResponse(
            {"error": True, "message": "Not authorized"}, status=403
        )

    credit_amount: int = request.POST.get("credit_amount")

    for user in User.objects.all():
        if user.redeemed_key is None:
            continue

        user.hosting_credit += credit_amount
        user.save()


# POST /api/v3/admin/table-data/users
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def table_data_users(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Get table data for users
    """
    users = []

    for user in User.objects.all():
        login_time = misc.seconds_to_readable_time(user.login_time)

        flags = get_flags(user)

        users.append(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email or "None",
                "loginData": f"{user.logins} logins, logged in for {login_time}",
                "key": user.redeemed_key.key if user.redeemed_key else "None",
                "accountType": user.account_type,
                "flags": ", ".join(flags),
                "hostingCredit": "Lifetime"
                if user.hosting_lifetime
                else misc.seconds_to_readable_time(user.hosting_credit * 60),
                "createdAt": misc.format_datetime(user.created_at),
            }
        )

    return http.JsonResponse({"error": False, "data": users})


# POST /api/v3/admin/table-data/online-users
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def table_data_online_users(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Get table data for users
    """
    one_minute_ago = timezone.now() - timezone.timedelta(minutes=1)

    user_models = User.objects.filter(last_selfbot_ping__gt=one_minute_ago)
    users = []

    for user in user_models.all():
        login_time = misc.seconds_to_readable_time(user.login_time)

        flags = get_flags(user)

        users.append(
            {
                "id": user.id,
                "username": user.username,
                "key": user.redeemed_key.key if user.redeemed_key else "None",
                "accountType": user.account_type,
                "flags": ", ".join(flags),
                "loggedInAt": misc.format_datetime(user.last_selfbot_login),
                "loginData": f"{user.logins} logins, logged in for {login_time}",
                "lastPingAt": misc.format_datetime(user.last_selfbot_ping),
            }
        )

    return http.JsonResponse({"error": False, "data": users})


# POST /api/v3/admin/table-data/keys
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
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
                "createdAt": misc.format_datetime(key.created_at),
                "createReason": key.create_reason,
                "redeemedBy": key.redeemed_by.username if key.redeemed_by else "None",
            }
        )

    return http.JsonResponse({"error": False, "data": key_data})


# POST /api/v3/admin/table-data/credit_keys
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def table_data_credit_keys(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Get table data for credit keys
    """
    key_data = []

    for key in CreditKey.objects.all():
        key_data.append(
            {
                "id": key.id,
                "key": key.key,
                "createdBy": key.created_by,
                "createdAt": misc.format_datetime(key.created_at),
                "createReason": key.create_reason,
                "creditAmount": "Lifetime"
                if key.is_lifetime
                else misc.seconds_to_readable_time(key.credit_amount * 60),
                "redeemedBy": key.redeemed_by.username if key.redeemed_by else "None",
            }
        )

    return http.JsonResponse({"error": False, "data": key_data})


# POST /api/v3/admin/table-data/orders
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
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
                "createdAt": misc.format_datetime(order.created_at),
                "rawJson": order.raw_json,
            }
        )

    return http.JsonResponse({"error": False, "data": order_data})


# POST /api/v3/admin/table-data/releases
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
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
                "createdAt": misc.format_datetime(release.created_at),
            }
        )

    return http.JsonResponse({"error": False, "data": releases_data})


# POST /api/v3/admin/action/user
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
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

    is_staff = user.is_staff or user.is_superuser

    if is_staff and not request.user.is_superuser:
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

    logs.create_entry(
        log_type="admin_user_action",
        user=request.user,
        info={
            "username": user.username,
            "user_id": user.id,
            "action": action,
            "data": data,
        },
    )

    return http.JsonResponse({"error": False})


# POST /api/v3/admin/action/key
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
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

    logs.create_entry(
        log_type="admin_user_action",
        user=request.user,
        info={
            "key": key.key,
            "key_id": key.id,
            "action": action,
            "type": "normal_key",
        },
    )

    return http.JsonResponse({"error": False})


# POST /api/v3/admin/action/credit_key
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def action_credit_key(request: http.HttpRequest) -> http.HttpResponse:
    """
    Credit key actions
    """
    action: str = request.POST.get("action")
    key_id: int = request.POST.get("key_id")

    try:
        key = CreditKey.objects.get(id=key_id)
    except Key.DoesNotExist:
        return http.JsonResponse(
            {"error": True, "message": "Key does not exist!"}, status=404
        )

    match action:
        case "delete":
            key.delete()

    logs.create_entry(
        log_type="admin_user_action",
        user=request.user,
        info={
            "key": key.key,
            "key_id": key.id,
            "action": action,
            "type": "credit_key",
        },
    )

    return http.JsonResponse({"error": False})
