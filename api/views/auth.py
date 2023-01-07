"""
Authentication views
"""
from django import http
from django.contrib import auth
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt

from ..utils import validation, logs
from ..utils import errors
from ..utils import stats
from ..utils import password_reset
from ..models import User


# /api/v3/auth/register
def register(request: http.HttpRequest) -> http.HttpResponse:
    """
    Create an account
    """
    username: str = request.POST["username"]
    password: str = request.POST["password"]
    captcha: str = request.POST["captcha"]

    if not validation.validate_captcha(request, captcha):
        return http.JsonResponse(
            {
                "status": 400,
                "error": "INVALID_CAPTCHA",
                "message": "Invalid captcha response.",
            },
            status=400,
        )

    validation_error = validation.validate_user(username, password)
    validation_error_str = validation.ValidationResult.to_string(
        validation_error,
    )

    match validation_error:
        case validation.ValidationResult.MissingField:
            return http.JsonResponse(
                {
                    "status": 400,
                    "error": validation_error_str,
                    "message": "Username or password cannot be empty.",
                },
                status=400,
            )
        case validation.ValidationResult.UsernameLength:
            return http.JsonResponse(
                {
                    "status": 400,
                    "error": validation_error_str,
                    "message": "Username must be between 3 and 40 characters.",
                },
                status=400,
            )
        case validation.ValidationResult.PasswordLength:
            return http.JsonResponse(
                {
                    "status": 400,
                    "error": validation_error_str,
                    "message": "Password must be at least 6 characters.",
                },
                status=400,
            )
        case validation.ValidationResult.UsernameInvalid:
            return http.JsonResponse(
                {
                    "status": 400,
                    "error": validation_error_str,
                    "message": "Username must include only letters,"
                    + " numbers, underscores and periods.",
                },
                status=400,
            )
        case validation.ValidationResult.UsernameTaken:
            return http.JsonResponse(
                {
                    "status": 400,
                    "error": validation_error_str,
                    "message": "An account with this username already exists.",
                },
                status=400,
            )

    user: User = User.objects.create_user(  # type: ignore
        username,
        "",
        password,
    )

    user.save()

    auth.login(request, user)

    logs.create_entry(
        log_type="register",
        user=user,
        info={"username": username},
    )

    return http.JsonResponse({"status": 200})


# /api/v3/auth/login
def login(request: http.HttpRequest) -> http.HttpResponse:
    """
    Login to an account
    """
    username: str = request.POST["username"]
    password: str = request.POST["password"]
    session = bool(request.POST["session"])
    rememberme = bool(request.POST["rememberme"])

    user = auth.authenticate(request, username=username, password=password)

    if user is None or not user.is_authenticated:
        return http.JsonResponse(
            {
                "status": 400,
                "error": "INVALID_CREDENTIALS",
                "message": "Invalid username or password.",
            },
            status=400,
        )

    if session:
        auth.login(request, user)
        request.session.set_expiry(0)

    if rememberme and session:
        # Make the session cookie expire after 30 days
        request.session.set_expiry(86400 * 30)

    return http.JsonResponse({"status": 200})


# /api/v3/auth/logout
def logout(request: http.HttpRequest) -> http.HttpResponse:
    """
    Log out of an account
    """
    auth.logout(request)

    return http.JsonResponse({"status": 200})


# /api/v3/auth/forgot-password
def forgot_password(request: http.HttpRequest) -> http.HttpResponse:
    """
    Send a password reset email
    """
    username = request.POST["username"]

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return http.JsonResponse(
            {
                "status": 400,
                "error": "INVALID_USERNAME",
                "message": "Invalid username.",
            },
            status=400,
        )

    if user.email == "":
        return http.JsonResponse(
            {
                "status": 400,
                "error": "NO_EMAIL",
                "message": "No email address associated with this account.",
            },
            status=400,
        )

    password_reset.send_reset_password_email(request, user)

    return http.JsonResponse({"status": 200})


# /api/v3/auth/reset-password
def reset_password(request: http.HttpRequest) -> http.HttpResponse:
    """
    Reset password
    """
    username = request.POST["username"]
    new_password = request.POST["new_password"]
    token = request.POST["token"]

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return http.JsonResponse(
            {
                "status": 400,
                "error": "INVALID_USERNAME",
                "message": "Invalid username.",
            },
            status=400,
        )

    if not password_reset.check_password_reset_token(user, token):
        return http.JsonResponse(
            {"status": 400, "error": "INVALID_TOKEN", "message": "Invalid token."},
            status=400,
        )

    validation_error = validation.validate_user(username, new_password)
    validation_error_str = validation.ValidationResult.to_string(
        validation_error,
    )
    match validation_error:
        case validation.ValidationResult.MissingField:
            return http.JsonResponse(
                {
                    "status": 400,
                    "error": validation_error_str,
                    "message": "Password cannot be empty.",
                },
                status=400,
            )
        case validation.ValidationResult.PasswordLength:
            return http.JsonResponse(
                {
                    "status": 400,
                    "error": validation_error_str,
                    "message": "Password must be at least 6 characters.",
                },
                status=400,
            )

    user.set_password(new_password)
    user.save()
    auth.update_session_auth_hash(request, user)
    return http.JsonResponse({"status": 200})


# /api/v3/auth/change-password
def change_password(request: http.HttpRequest) -> http.HttpResponse:
    """
    Change password
    """
    current_password = request.POST["current_password"]
    new_password = request.POST["new_password"]
    if not request.user.check_password(current_password):
        return http.JsonResponse(
            {
                "status": 400,
                "error": "INVALID_CREDENTIALS",
                "message": "The current password is incorrect.",
            },
            status=400,
        )
    validation_error = validation.validate_user(request.user.username, new_password)
    match validation_error:
        case validation.ValidationResult.MissingField:
            return http.JsonResponse(
                {
                    "status": 400,
                    "error": validation.ValidationResult.to_string(validation_error),
                    "message": "Password cannot be empty.",
                },
                status=400,
            )
        case validation.ValidationResult.PasswordLength:
            return http.JsonResponse(
                {
                    "status": 400,
                    "error": validation.ValidationResult.to_string(validation_error),
                    "message": "Password must be at least 6 characters.",
                },
                status=400,
            )
    request.user.set_password(new_password)
    request.user.save()
    auth.update_session_auth_hash(request, request.user)
    return http.JsonResponse({"status": 200})


# /api/v3/auth/get-user
def get_user(request: http.HttpRequest) -> http.HttpResponse:
    """
    Get data about the current logged in user
    """
    if not request.user.is_authenticated:
        return errors.login_required()

    return http.JsonResponse(
        {
            "status": 200,
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "is_staff": request.user.is_staff or request.user.is_superuser,
                "is_tester": request.user.is_tester,
                "account_type": request.user.account_type,
                "logins": request.user.logins,
                "date_joined": request.user.date_joined,
                "login_time": request.user.login_time,
                "key": getattr(request.user.redeemed_key, "key", "None"),
                "free_trial_expiry": request.user.free_trial_expiry,
                "last_selfbot_login": request.user.last_selfbot_login,
            },
        }
    )


# /api/v3/auth/set-email
def set_email(request: http.HttpRequest) -> http.HttpResponse:
    """
    Set email address
    """
    email = request.POST["email"]
    password = request.POST["password"]
    user = request.user
    if not user.check_password(password):
        return http.JsonResponse(
            {
                "status": 400,
                "error": "INVALID_CREDENTIALS",
                "message": "The password is incorrect.",
            },
            status=400,
        )
    try:
        validate_email(email)
    except ValidationError:
        return http.JsonResponse(
            {
                "status": 400,
                "error": "INVALID_EMAIL",
                "message": "Invalid email address.",
            },
            status=400,
        )
    user.email = email
    user.save()
    return http.JsonResponse({"status": 200})


# /api/v3/auth/auth
@csrf_exempt
def auth_view(request: http.HttpRequest) -> http.HttpResponse:
    """
    Auth view
    """
    username = request.POST["username"]
    password = request.POST["password"]
    client_type = request.POST["client_type"]
    user: User = auth.authenticate(request, username=username, password=password)  # type: ignore
    match client_type:
        case "ui":
            if user is None or not user.is_authenticated:
                return http.JsonResponse(
                    {
                        "status": 400,
                        "error": "INVALID_CREDENTIALS",
                        "message": "Invalid username or password.",
                    },
                    status=400,
                )

            return http.JsonResponse(
                {
                    "status": 200,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "is_staff": user.is_staff or user.is_superuser,
                        "is_tester": user.is_tester,
                        "account_type": user.account_type,
                        "logins": user.logins,
                        "date_joined": user.date_joined,
                        "login_time": user.login_time,
                        "key": getattr(user.redeemed_key, "key", "None"),
                        "free_trial_expiry": user.free_trial_expiry,
                        "last_selfbot_login": user.last_selfbot_login,
                    },
                    "stats": stats.all_stats(user),
                }
            )

    return http.JsonResponse(
        {
            "status": 400,
            "error": "INVALID_CLIENT_TYPE",
            "message": "Invalid client type.",
        },
        status=400,
    )
