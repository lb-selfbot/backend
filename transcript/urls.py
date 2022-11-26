"""
Transcript urls
"""
from django.urls import path

from . import views

urlpatterns = [
    path("<str:code>", views.render_transcript, name="Render Transcript")
]
