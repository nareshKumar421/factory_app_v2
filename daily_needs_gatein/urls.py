from django.urls import path
from .views import DailyNeedGateCompleteAPI, DailyNeedGateEntryCreateAPI,CategoryListAPI

urlpatterns = [
    path(
        "gate-entries/<int:gate_entry_id>/daily-need/",
        DailyNeedGateEntryCreateAPI.as_view()
    ),
    path(
        "gate-entries/<int:gate_entry_id>/complete/",
        DailyNeedGateCompleteAPI.as_view()
    ),
    path("gate-entries/daily-need/categories/", CategoryListAPI.as_view()),
]
