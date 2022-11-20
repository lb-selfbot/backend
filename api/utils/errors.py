"""
API errors
"""
import typing

from django import http


def login_required() -> http.HttpResponse:
    """
    Login required error
    """
    return http.JsonResponse(
        {
            "status": 401,
            "error": "LOGIN_REQUIRED",
            "reason": "You must be logged in to perform this action.",
        },
        status=401,
    )


def method_not_allowed(allowed_methods: typing.List[str]) -> http.HttpResponse:
    """
    Method not allowed error
    """
    return http.JsonResponse(
        {
            "error": True,
            "reason": "Method not allowed",
            "allowed_methods": allowed_methods,
        },
        status=405,
    )


def invalid_header(
    header_name: str, valid_values: typing.List[str]
) -> http.HttpResponse:
    """
    Invalid header error
    """
    return http.JsonResponse(
        {
            "error": True,
            "reason": f"\"{header_name}\" header must be one of: {', '.join(valid_values)}",
            "valid_values": valid_values,
        },
        status=400,
    )


def invalid_json() -> http.HttpResponse:
    """
    Invalid JSON error
    """
    return http.JsonResponse(
        {
            "error": True,
            "reason": "Invalid JSON body",
        },
        status=400,
    )


def missing_or_invalid_field(field: str) -> http.HttpResponse:
    """
    Missing or invalid field error
    """
    return http.JsonResponse(
        {
            "error": True,
            "reason": f"Missing or invalid field: {field}",
        },
        status=400,
    )


def invalid_credentials() -> http.HttpResponse:
    """
    Invalid credentials error
    """
    return http.JsonResponse(
        {
            "error": True,
            "reason": "Invalid credentials",
        },
        status=401,
    )


def admin_required() -> http.HttpResponse:
    """
    Admin required error
    """
    return http.JsonResponse(
        {
            "error": True,
            "reason": "You are not allowed to perform this action.",
        },
        status=403,
    )
