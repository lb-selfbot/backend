"""
Admin API views
"""
import os

from django import http

from lightningbot import settings
from ..utils import keys
from ..models import Release

# POST /api/v3/admin/create-key
def create_key(request: http.HttpRequest) -> http.HttpResponse:
    """
    Create a new API key for a user.
    """
    key = keys.create_key(create_reason="API Request", created_by=request.user.username)

    return http.JsonResponse({"error": False, "key": key.key})


# POST /api/v3/admin/create-release
def create_release(request: http.HttpRequest) -> http.HttpResponse:
    """
    Create a new release
    """
    version = request.POST.get("version")
    branch = request.POST.get("branch")
    changelog = request.POST.get("changelog")
    filename = request.POST.get("filename")
    executable = request.FILES.get("executable")

    # Check if any of the fields are None
    if any(
        map(lambda x: x is None, [version, branch, changelog, filename, executable])
    ):
        return http.JsonResponse(
            {"error": True, "message": "Missing required fields."}, status=400
        )

    filename = filename.replace("/", "").replace("\\", "")

    # save the file to static folder
    releases_path = os.path.join(settings.STATIC_ROOT, "releases")
    os.makedirs(releases_path, exist_ok=True)
    with open(f"{releases_path}/{filename}", "wb+") as file:
        for chunk in executable.chunks():
            file.write(chunk)

    Release.objects.create(
        version=version,
        branch=branch,
        changelog=changelog,
        filename=filename,
    )

    return http.JsonResponse({"error": False, "release": ""})
