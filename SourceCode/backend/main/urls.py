"""main/urls.py — Root URL configuration."""

from django.urls import path, include

urlpatterns = [
    path('user/api/', include('auths.urls')),
    # Workflow API
    path('workflow/api/', include('workflow.urls')),
    # Chatbot API
    path('chatbot/api/', include('chatbot.urls')),
    # Dashboard API
    path('dashboard/api/', include('dashboard.urls')),
    # Destinations API
    path('destinations/api/', include('destinations.urls')),
    # Auths API
    path('auths/api/', include('auths.urls')),
]

