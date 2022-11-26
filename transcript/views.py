"""
Transcript views
"""
from django import http

from api.models import Transcript

def render_transcript(request: http.HttpRequest, code: str) -> http.HttpResponse:
    """
    Render a ticket transcript
    """
    if request.method != "GET":
        return http.HttpResponseNotAllowed(["GET"])

    if request.headers.get("X-Forwarded-Host") != "transcript.lightning-bot.com":
        return http.HttpResponseForbidden()

    transcript = Transcript.objects.filter(code=code).first()
    if transcript is None:
        return http.HttpResponseNotFound()

    return http.HttpResponse(transcript.html)
