from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('update-preferences/', views.update_preferences, name='update_preferences'),
    path('update-profile/', views.update_profile, name='update_profile'),
]
