"""
chatbot/urls.py
URL patterns for the Traplanner chatbot API.
All paths are relative to the prefix defined in main/urls.py (chatbot/api/).
"""

from django.urls import path
from . import routes

urlpatterns = [
    path("health/", routes.health, name="chatbot_health"),
    path("trips/<str:user_id>/", routes.list_trips, name="chatbot_list_trips"),
    path("trip/<str:trip_id>/", routes.get_trip, name="chatbot_get_trip"),
    path("chat/", routes.chat, name="chatbot_chat"),
    path("memory/<str:user_id>/", routes.clear_memory, name="chatbot_clear_memory"),
]
