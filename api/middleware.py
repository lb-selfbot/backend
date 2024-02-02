"""
Middlewares for the API
"""

import os
import json
import typing

from django import http
from django.contrib import auth

from . import routes
from .utils import errors


class ExceptionMiddleware:
    def __init__(self, get_response: typing.Callable):
        self.get_response = get_response

    def __call__(self, request: http.HttpRequest) -> http.HttpResponse:
        try:
            response = self.get_response(request)
        except Exception as e:
            response = http.HttpResponseServerError("Oops! Something went wrong: " + str(e))
        return response


class ApiMiddleware:
    """
    Process requests so the API can handle them
    """

    def __init__(self, get_response: typing.Callable):
        self.get_response = get_response

    def get_route(self, path: str) -> typing.Optional[routes.Route]:
        """
        Get the route for the given path
        """
        for route in routes.routes:
            match = route.get_path().resolve(path)

            if match is not None:
                return route

        return None

    def __call__(self, request: http.HttpRequest) -> http.HttpResponse:
        # Only process API requests
        if not request.path.startswith("/api"):
            return self.get_response(request)

        # Don't process WebSocket requests
        if request.path.startswith("/api/v3/ws"):
            return self.get_response(request)

        api_path = request.path[5:].lower()

        api_route = self.get_route(api_path)

        if api_route is None:
            return http.HttpResponseNotFound()

        method = str(request.method).upper()

        if method not in api_route.methods:
            return errors.method_not_allowed(api_route.methods)

        if routes.RouteFlags.JSON_REQUIRED in api_route.flags:
            # Refuse non-JSON requests
            if not str(request.META.get("CONTENT_TYPE")).startswith("application/json"):
                return errors.invalid_header("Content-Type", ["application/json"])

            # Try to parse the body as JSON
            try:
                request.POST = json.loads(request.body.decode("utf-8"))
            except json.JSONDecodeError:
                return errors.invalid_json()

            # Check if required fields are present
            for field in api_route.required_json_fields:
                field_type, field_name = field.split(":")
                post_field = request.POST.get(field_name)
                if type(post_field).__name__ != field_type:
                    return errors.missing_or_invalid_field(field_name)

        if routes.RouteFlags.LOGIN_REQUIRED in api_route.flags:
            # Check if the user is logged in
            # if not, check if username and password are provided
            if not request.user.is_authenticated:
                if "username" not in request.POST or "password" not in request.POST:
                    return errors.login_required()

                # Try to log in with username and password
                username: str = request.POST.get("username", "")
                password: str = request.POST.get("password", "")

                user = auth.authenticate(request, username=username, password=password)

                if user is None or not user.is_authenticated:
                    return errors.invalid_credentials()

                request.user = user

        if routes.RouteFlags.ADMIN_REQUIRED in api_route.flags:
            if not request.user.is_staff and not request.user.is_superuser:
                return errors.admin_required()

        if routes.RouteFlags.DISCORD_BOT in api_route.flags:
            if request.headers.get("authorization") != os.environ["DISCORD_BOT_TOKEN"]:
                return errors.invalid_credentials()

        return self.get_response(request)
