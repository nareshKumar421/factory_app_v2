from django.urls import path
from driver_management.views import (
    DriverListCreateAPI,
    DriverDetailAPI,
    DriverNameListAPI
)

urlpatterns = [
    path("drivers/", DriverListCreateAPI.as_view()),
    path("drivers/<int:id>/", DriverDetailAPI.as_view()),
    path("drivers/names/", DriverNameListAPI.as_view()),

]
