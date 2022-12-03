"""
Routes for the API
"""
import typing
from enum import Flag, auto

from django.views.decorators.csrf import csrf_exempt
from django.urls import path, resolvers

from lightningbot import settings
from . import views


class RouteFlags(Flag):
    """
    Flags for the API routes
    """

    NONE = auto()
    LOGIN_REQUIRED = auto()
    ADMIN_REQUIRED = auto()
    JSON_REQUIRED = auto()
    DISCORD_BOT = auto()


class Route:
    """
    An API route
    """

    def __init__(
        self,
        route: str,
        view: typing.Callable,
        name: str = "",
        methods: typing.Optional[typing.List[str]] = None,
        required_json_fields: typing.Optional[typing.List[str]] = None,
        flags: RouteFlags = RouteFlags.NONE,
    ):
        if methods is None:
            methods = []
        if required_json_fields is None:
            required_json_fields = []
        self.route = route
        self.view = view
        self.name = name
        self.methods = methods
        self.required_json_fields = required_json_fields
        self.flags = flags

    def get_path(self) -> (resolvers.URLPattern | resolvers.RoutePattern):
        """
        Get the Django path for this route
        """
        if settings.DEBUG:
            return path(self.route, csrf_exempt(self.view), name=self.name)
        return path(self.route, self.view, name=self.name)

routes = [
    # Stats
    Route(
        "v3/stats/all",
        views.stats.all_stats,
        name="All Stats",
        methods=["GET"],
    ),
    # Misc
    Route(
        "v3/misc/fml",
        views.misc.fml,
        name="FML",
        methods=["GET"],
    ),
    Route(
        "v3/misc/riddle",
        views.misc.riddle,
        name="Riddle",
        methods=["GET"],
    ),
    Route(
        "v3/misc/joke",
        views.misc.joke,
        name="Joke",
        methods=["GET"],
    ),
    Route(
        "v3/misc/wyr",
        views.misc.wyr,
        name="Would You Rather",
        methods=["GET"],
    ),
    Route(
        "v3/misc/topic",
        views.misc.topic,
        name="Topic",
        methods=["GET"],
    ),
    Route(
        "v3/misc/search",
        views.misc.search,
        name="Google Search",
        methods=["GET"],
    ),
    Route(
        "v3/misc/ccgen",
        views.misc.ccgen,
        name="Credit Card Gen",
        methods=["GET"],
    ),
    # Authentication
    Route(
        "v3/auth/register",
        views.auth.register,
        name="Register",
        methods=["POST"],
        required_json_fields=["str:username", "str:password", "str:captcha"],
        flags=RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/auth/login",
        views.auth.login,
        name="Login",
        methods=["POST"],
        required_json_fields=[
            "str:username",
            "str:password",
            "bool:session",
            "bool:rememberme",
        ],
        flags=RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/auth/logout",
        views.auth.logout,
        name="Logout",
        methods=["POST"],
        flags=RouteFlags.LOGIN_REQUIRED,
    ),
    Route(
        "v3/auth/forgot-password",
        views.auth.forgot_password,
        name="Forgot Password",
        methods=["POST"],
        required_json_fields=["str:username"],
        flags=RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/auth/reset-password",
        views.auth.reset_password,
        name="Reset Password",
        methods=["POST"],
        required_json_fields=["str:username", "str:password", "str:token"],
        flags=RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/auth/change-password",
        views.auth.change_password,
        name="Change Password",
        methods=["POST"],
        required_json_fields=["str:current_password", "str:new_password"],
        flags=RouteFlags.LOGIN_REQUIRED | RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/auth/get-user",
        views.auth.get_user,
        name="Get User Data",
        methods=["GET"],
        flags=RouteFlags.LOGIN_REQUIRED,
    ),
    Route(
        "v3/auth/set-email",
        views.auth.set_email,
        name="Set Email",
        methods=["POST"],
        required_json_fields=["str:email", "str:password"],
        flags=RouteFlags.LOGIN_REQUIRED | RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/auth/auth",
        views.auth.auth_view,
        name="Auth",
        methods=["POST"],
        required_json_fields=[
            "str:username",
            "str:password",
            "str:client_type",
        ],
        flags=RouteFlags.JSON_REQUIRED,
    ),
    # Selfbot
    Route(
        "v3/selfbot/reset-hwid",
        views.selfbot.reset_hwid,
        name="Reset HWID",
        methods=["POST"],
        flags=RouteFlags.LOGIN_REQUIRED,
    ),
    Route(
        "v3/selfbot/redeem-key",
        views.selfbot.redeem_key,
        name="Redeem Key",
        methods=["POST"],
        required_json_fields=["str:key"],
        flags=RouteFlags.LOGIN_REQUIRED | RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/selfbot/check-version",
        views.selfbot.check_version,
        name="Check Version",
        methods=["POST"],
        required_json_fields=["str:branch", "str:version"],
        flags=RouteFlags.JSON_REQUIRED,
    ),
    # PayPal
    Route(
        "v3/paypal/create-order",
        views.paypal.create_order,
        name="Create Order",
        methods=["POST"],
        flags=RouteFlags.LOGIN_REQUIRED,
    ),
    Route(
        "v3/paypal/capture-order",
        views.paypal.capture_order,
        name="Capture Order",
        methods=["POST"],
        required_json_fields=["str:order_id"],
        flags=RouteFlags.LOGIN_REQUIRED | RouteFlags.JSON_REQUIRED,
    ),
    # Admin
    Route(
        "v3/admin/create-key",
        views.admin.create_key,
        name="Create Key",
        methods=["POST"],
        flags=RouteFlags.LOGIN_REQUIRED | RouteFlags.ADMIN_REQUIRED,
    ),
    Route(
        "v3/admin/create-release",
        views.admin.create_release,
        name="Create Release",
        methods=["POST"],
    ),
    # Discord Bot
    Route(
        "v3/discord-bot/create-key",
        views.discord_bot.create_key,
        name="Create Key",
        methods=["POST"],
        required_json_fields=["str:created_by"],
        flags=RouteFlags.DISCORD_BOT | RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/discord-bot/check-key",
        views.discord_bot.check_key,
        name="Check Key",
        methods=["GET"],
        flags=RouteFlags.DISCORD_BOT,
    ),
    Route(
        "v3/discord-bot/create-transcript",
        views.discord_bot.create_transcript,
        name="Create Transcript",
        methods=["POST"],
        required_json_fields=["str:html"],
        flags=RouteFlags.DISCORD_BOT | RouteFlags.JSON_REQUIRED,
    )
]
