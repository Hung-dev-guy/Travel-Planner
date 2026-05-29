"""trips/urls.py — URL patterns for the trips (pipeline) app."""

from django.urls import path
from . import views

urlpatterns = [
    path("pipeline/run", views.generate_plan),
    path("pipeline/health", views.health_check),
]
