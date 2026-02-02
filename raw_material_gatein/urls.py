from django.urls import path
from .views import (
    ReceivePOAPI,
    GatePOListAPI,
    CompleteGateEntryAPI,
)

urlpatterns = [
    path(
        "gate-entries/<int:gate_entry_id>/po-receipts/",
        ReceivePOAPI.as_view()
    ),
    path(
        "gate-entries/<int:gate_entry_id>/po-receipts/view/",
        GatePOListAPI.as_view()
    ),
    path(
        "gate-entries/<int:gate_entry_id>/complete/",
        CompleteGateEntryAPI.as_view()
    ),
]
