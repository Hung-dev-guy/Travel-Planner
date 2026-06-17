"""dashboard/urls.py"""
from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health, name="dashboard_health"),
    path("stats/<str:user_id>/", views.dashboard_stats, name="dashboard_stats"),
]
