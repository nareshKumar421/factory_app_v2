from django.urls import path
from weighment.views import (
    WeighmentCreateUpdateAPI,
    WeighmentDetailAPI,
)

urlpatterns = [
    path(
        "gate-entries/<int:gate_entry_id>/weighment/",
        WeighmentCreateUpdateAPI.as_view()
    ),
    path(
        "gate-entries/<int:gate_entry_id>/weighment/view/",
        WeighmentDetailAPI.as_view()
    ),
]
