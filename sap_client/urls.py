from django.urls import path
from .views import OpenPOListAPI, POItemListAPI

urlpatterns = [
    path("open-pos/", OpenPOListAPI.as_view()),
    path("open-pos/<str:po_number>/items/", POItemListAPI.as_view()),
]
