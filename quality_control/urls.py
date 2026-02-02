from django.urls import path
from .views import (
    QCCreateUpdateAPI,
    QCDetailAPI,
)

urlpatterns = [
    path(
        "po-items/<int:po_item_id>/qc/",
        QCCreateUpdateAPI.as_view()
    ),
    path(
        "po-items/<int:po_item_id>/qc/view/",
        QCDetailAPI.as_view()
    ),
]
