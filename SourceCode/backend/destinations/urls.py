from django.urls import path
from . import views

urlpatterns = [
    path('locations/', views.list_locations, name='list_locations'),
    path('provinces/', views.get_provinces, name='get_provinces'),
    path('wards/', views.get_wards, name='get_wards'),
    path('transport/add/', views.add_transport, name='add_transport'),
    path('locations/add/', views.add_location, name='add_location'),
    path('locations/review/', views.add_review, name='add_review'),
    path('locations/reviews/', views.get_reviews, name='get_reviews'),
    path('locations/trips/', views.get_trips_by_location, name='get_trips_by_location'),
    path('locations/edit/', views.edit_location, name='edit_location'),
    path('locations/delete/', views.delete_location, name='delete_location'),
]
