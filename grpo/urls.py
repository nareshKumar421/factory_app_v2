from django.urls import path
from .views import (
    PendingGRPOListAPI,
    GRPOPreviewAPI,
    PostGRPOAPI,
    GRPOPostingHistoryAPI,
    GRPOPostingDetailAPI
)

urlpatterns = [
    # List pending GRPO entries
    path("pending/", PendingGRPOListAPI.as_view(), name="grpo-pending"),

    # Preview GRPO data for a gate entry
    path("preview/<int:vehicle_entry_id>/", GRPOPreviewAPI.as_view(), name="grpo-preview"),

    # Post GRPO to SAP
    path("post/", PostGRPOAPI.as_view(), name="grpo-post"),

    # GRPO posting history
    path("history/", GRPOPostingHistoryAPI.as_view(), name="grpo-history"),

    # GRPO posting detail
    path("<int:posting_id>/", GRPOPostingDetailAPI.as_view(), name="grpo-detail"),
]
