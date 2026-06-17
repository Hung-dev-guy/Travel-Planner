from django.urls import path
from . import views

urlpatterns = [
    path('locations/', views.list_locations, name='list_locations'),
    path('provinces/', views.get_provinces, name='get_provinces'),
    path('wards/', views.get_wards, name='get_wards'),
]
