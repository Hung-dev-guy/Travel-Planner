from django.urls import path
from . import views

urlpatterns = [
    path("run", views.run_pipeline, name="run_pipeline"),
    path("save-trip", views.save_trip, name="save_trip"),
    path("trip/<str:trip_id>/", views.get_trip, name="get_trip"),
    path("trip/<str:trip_id>/delete", views.delete_trip, name="delete_trip"),
    path("health", views.health, name="pipeline_health"),
]
