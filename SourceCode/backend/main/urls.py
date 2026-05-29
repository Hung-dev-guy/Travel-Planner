"""main/urls.py — Root URL configuration."""

from django.urls import path, include

urlpatterns = [
    path("api/", include("trips.urls")),
]
