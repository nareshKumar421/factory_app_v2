from django.urls import path
from .views import OpenPOListAPI, POItemListAPI, CreateGRPOAPI

urlpatterns = [
    path("open-pos/", OpenPOListAPI.as_view()),
    path("open-pos/<str:po_number>/items/", POItemListAPI.as_view()),
    path("grpo/", CreateGRPOAPI.as_view(), name="create-grpo"),
]
