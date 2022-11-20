"""
Stats API views
"""
from django import http

from api.utils import stats


# GET /api/v3/stats/all
def all_stats(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Get all stats
    """
    return http.JsonResponse(
        {
            "error": False,
            "stats": stats.all_stats(),
        }
    )
