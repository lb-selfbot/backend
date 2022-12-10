"""
Admin API views
"""
import os

from django import http

from lightningbot import settings
from ..utils import keys, github
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

    # Check if any of the fields are None
    if any(map(lambda x: x is None, [version, branch, changelog])):
        return http.JsonResponse(
            {"error": True, "message": "Missing required fields."}, status=400
        )

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
