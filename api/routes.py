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

    def get_path(self) -> resolvers.URLPattern | resolvers.RoutePattern:
        """
        Get the Django path for this route
        """

        return path(self.route, csrf_exempt(self.view), name=self.name)


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
        "v3/misc/breaking-bad-quote",
        views.misc.breaking_bad_quote,
        name="Breaking Bad Quote",
        methods=["GET"],
    ),
    Route(
        "v3/misc/game-of-thrones-quote",
        views.misc.game_of_thrones_quote,
        name="Game of Thrones quote",
        methods=["GET"],
    ),
    Route(
        "v3/misc/lucifer-quote",
        views.misc.lucifer_quote,
        name="Lucifer quote",
        methods=["GET"],
    ),
    Route(
        "v3/misc/stranger-things-quote",
        views.misc.stranger_things_quote,
        name="Stranger Things quote",
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
    Route(
        "v3/misc/meme",
        views.misc.meme,
        name="Meme Gen",
        methods=["GET"],
    ),
    # Authentication
    Route(
        "v3/auth/register",
        views.auth.register,
        name="Register",
        methods=["POST"],
        required_json_fields=["str:username", "str:password", "str:captcha_token"],
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
            "str:captcha_token",
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
        required_json_fields=["str:username", "str:captcha_token"],
        flags=RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/auth/reset-password",
        views.auth.reset_password,
        name="Reset Password",
        methods=["POST"],
        required_json_fields=[
            "str:username",
            "str:new_password",
            "str:token",
            "str:captcha_token",
        ],
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
        required_json_fields=["str:key", "str:captcha_token"],
        flags=RouteFlags.LOGIN_REQUIRED | RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/selfbot/redeem-credit-key",
        views.selfbot.redeem_credit_key,
        name="Redeem Credit Key",
        methods=["POST"],
        required_json_fields=["str:key", "str:captcha_token"],
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
    Route(
        "v3/selfbot/enable-hosting",
        views.selfbot.enable_hosting,
        name="Enable Hosting",
        methods=["POST"],
        required_json_fields=["str:token"],
        flags=RouteFlags.JSON_REQUIRED | RouteFlags.LOGIN_REQUIRED,
    ),
    Route(
        "v3/selfbot/disable-hosting",
        views.selfbot.disable_hosting,
        name="Disable Hosting",
        methods=["POST"],
        flags=RouteFlags.LOGIN_REQUIRED,
    ),
    Route(
        "v3/selfbot/hosting/list-files",
        views.selfbot.hosting_list_files,
        name="Hosting - List Files",
        methods=["GET"],
        flags=RouteFlags.LOGIN_REQUIRED,
    ),
    Route(
        "v3/selfbot/hosting/delete-folder",
        views.selfbot.hosting_delete_folder,
        name="Hosting - Delete Folder",
        methods=["POST"],
        required_json_fields=["str:folder_path"],
        flags=RouteFlags.LOGIN_REQUIRED | RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/selfbot/hosting/download-file",
        views.selfbot.hosting_download_file,
        name="Hosting - Download File",
        methods=["GET"],
        flags=RouteFlags.LOGIN_REQUIRED,
    ),
    Route(
        "v3/selfbot/hosting/delete-file",
        views.selfbot.hosting_delete_file,
        name="Hosting - Delete File",
        methods=["POST"],
        required_json_fields=["str:file_path"],
        flags=RouteFlags.LOGIN_REQUIRED | RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/selfbot/start-params",
        views.selfbot.start_params,
        name="Start Params",
        methods=["POST"],
    ),
    Route(
        "v3/selfbot/gen-image-key",
        views.selfbot.gen_image_key,
        name="Gen Image Key",
        methods=["POST"],
        required_json_fields=["str:image_url"],
        flags=RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/selfbot/ocr",
        views.selfbot.ocr,
        name="OCR",
        methods=["POST"],
        required_json_fields=["str:image"],
        flags=RouteFlags.LOGIN_REQUIRED | RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/selfbot/obfuscate",
        views.selfbot.obfuscate,
        name="Obfuscate",
        methods=["POST"],
        required_json_fields=["str:lang", "str:code"],
        flags=RouteFlags.JSON_REQUIRED,
    ),
    # PayPal
    Route(
        "v3/paypal/create-order",
        views.paypal.create_order,
        name="Create Order",
        methods=["POST"],
        required_json_fields=["str:captcha_token"],
        flags=RouteFlags.LOGIN_REQUIRED | RouteFlags.JSON_REQUIRED,
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
        "v3/admin/create-credit-key",
        views.admin.create_credit_key,
        name="Create Credit Key",
        methods=["POST"],
        required_json_fields=["int:credit_amount", "str:is_lifetime"],
        flags=RouteFlags.LOGIN_REQUIRED
        | RouteFlags.ADMIN_REQUIRED
        | RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/admin/create-release",
        views.admin.create_release,
        name="Create Release",
        methods=["POST"],
        required_json_fields=["str:version", "str:branch", "str:changelog"],
        flags=RouteFlags.LOGIN_REQUIRED
        | RouteFlags.ADMIN_REQUIRED
        | RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/admin/delete-release",
        views.admin.delete_release,
        name="Delete Release",
        methods=["POST"],
        required_json_fields=["int:release_id"],
        flags=RouteFlags.LOGIN_REQUIRED
        | RouteFlags.ADMIN_REQUIRED
        | RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/admin/deploy-docs",
        views.admin.deploy_docs,
        name="Deploy Docs",
        methods=["POST"],
        flags=RouteFlags.LOGIN_REQUIRED
        | RouteFlags.ADMIN_REQUIRED
        | RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/admin/provide-hosting-credit",
        views.admin.provide_hosting_credit,
        name="Provide Hosting Credit",
        methods=["POST"],
        required_json_fields=["int:credit_amount"],
        flags=RouteFlags.LOGIN_REQUIRED
        | RouteFlags.ADMIN_REQUIRED
        | RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/admin/table-data/users",
        views.admin.table_data_users,
        name="Table Data - Users",
        methods=["GET"],
        flags=RouteFlags.LOGIN_REQUIRED | RouteFlags.ADMIN_REQUIRED,
    ),
    Route(
        "v3/admin/table-data/online-users",
        views.admin.table_data_online_users,
        name="Table Data - Online Users",
        methods=["GET"],
        flags=RouteFlags.LOGIN_REQUIRED | RouteFlags.ADMIN_REQUIRED,
    ),
    Route(
        "v3/admin/table-data/keys",
        views.admin.table_data_keys,
        name="Table Data - Keys",
        methods=["GET"],
        flags=RouteFlags.LOGIN_REQUIRED | RouteFlags.ADMIN_REQUIRED,
    ),
    Route(
        "v3/admin/table-data/credit-keys",
        views.admin.table_data_credit_keys,
        name="Table Data - Credit Keys",
        methods=["GET"],
        flags=RouteFlags.LOGIN_REQUIRED | RouteFlags.ADMIN_REQUIRED,
    ),
    Route(
        "v3/admin/table-data/orders",
        views.admin.table_data_orders,
        name="Table Data - Orders",
        methods=["GET"],
        flags=RouteFlags.LOGIN_REQUIRED | RouteFlags.ADMIN_REQUIRED,
    ),
    Route(
        "v3/admin/table-data/releases",
        views.admin.table_data_releases,
        name="Table Data - Releases",
        methods=["GET"],
        flags=RouteFlags.LOGIN_REQUIRED | RouteFlags.ADMIN_REQUIRED,
    ),
    Route(
        "v3/admin/action/user",
        views.admin.action_user,
        name="Table Action - User",
        methods=["POST"],
        required_json_fields=["str:action", "int:user_id", "str:data"],
        flags=RouteFlags.LOGIN_REQUIRED
        | RouteFlags.ADMIN_REQUIRED
        | RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/admin/action/key",
        views.admin.action_key,
        name="Table Action - Key",
        methods=["POST"],
        required_json_fields=["str:action", "int:key_id"],
        flags=RouteFlags.LOGIN_REQUIRED
        | RouteFlags.ADMIN_REQUIRED
        | RouteFlags.JSON_REQUIRED,
    ),
    Route(
        "v3/admin/action/credit-key",
        views.admin.action_credit_key,
        name="Table Action - Credit Key",
        methods=["POST"],
        required_json_fields=["str:action", "int:key_id"],
        flags=RouteFlags.LOGIN_REQUIRED
        | RouteFlags.ADMIN_REQUIRED
        | RouteFlags.JSON_REQUIRED,
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
    ),
    # Image Generation
    Route(
        "v3/imagegen/achievement",
        views.imagegen.achievement,
        name="Achievement",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/amiajoke",
        views.imagegen.amiajoke,
        name="Am I A Joke To You",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/bad",
        views.imagegen.bad,
        name="Bad",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/calling",
        views.imagegen.calling,
        name="Calling",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/captcha",
        views.imagegen.captcha,
        name="Captcha",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/didyoumean",
        views.imagegen.didyoumean,
        name="Did You Mean",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/drake",
        views.imagegen.drake,
        name="Drake",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/facts",
        views.imagegen.facts,
        name="Facts",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/filter",
        views.imagegen.filter_image,
        name="Filter",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/floor",
        views.imagegen.floor,
        name="Floor",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/jokeoverhead",
        views.imagegen.jokeoverhead,
        name="Joke Overhead",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/trash",
        views.imagegen.trash,
        name="Trash",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/pornhub",
        views.imagegen.pornhub,
        name="Pornhub",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/salty",
        views.imagegen.salty,
        name="Salty",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/scroll",
        views.imagegen.scroll,
        name="Scroll",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/shame",
        views.imagegen.shame,
        name="Shame",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/ship",
        views.imagegen.ship,
        name="Ship",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/what",
        views.imagegen.what,
        name="What",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/speechbubble",
        views.imagegen.speechbubble,
        name="Speechbubble",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/quote",
        views.imagegen.quote,
        name="Quote",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/discordquote",
        views.imagegen.discordquote,
        name="Discordquote",
        methods=["GET"],
    ),
    Route(
        "v3/imagegen/view/<str:image>",
        views.imagegen.view_image,
        name="View Image",
        methods=["GET"],
    ),
]
