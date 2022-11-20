"""
Admin API views
"""
from django import http

from ..utils import keys

# POST /api/v3/admin/create-key
def create_key(request):
    """
    Create a new API key for a user.
    """
    key = keys.create_key(create_reason="API Request", created_by=request.user.username)

    return http.JsonResponse({"error": False, "key": key.key})
