"""
Stats API views
"""
from django import http
from django_ratelimit.decorators import ratelimit

from api.utils import stats


# GET /api/v3/stats/all
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def all_stats(request: http.HttpRequest) -> http.HttpResponse:
    """
    Get all stats
    """
    return http.JsonResponse(
        {
            "error": False,
            "stats": stats.all_stats(request.user),
        }
    )
