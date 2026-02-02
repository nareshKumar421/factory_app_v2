from django.urls import path
from .views import (
    ConstructionGateEntryCreateAPI,
    ConstructionGateEntryUpdateAPI,
    ConstructionGateCompleteAPI,
    ConstructionMaterialCategoryListAPI
)

urlpatterns = [
    # Create/Read construction entry
    path(
        "gate-entries/<int:gate_entry_id>/construction/",
        ConstructionGateEntryCreateAPI.as_view(),
        name="construction-entry-create"
    ),
    # Update construction entry
    path(
        "gate-entries/<int:gate_entry_id>/construction/update/",
        ConstructionGateEntryUpdateAPI.as_view(),
        name="construction-entry-update"
    ),
    # Complete/lock gate entry
    path(
        "gate-entries/<int:gate_entry_id>/complete/",
        ConstructionGateCompleteAPI.as_view(),
        name="construction-complete"
    ),
    # List construction material categories (for dropdown)
    path(
        "gate-entries/construction/categories/",
        ConstructionMaterialCategoryListAPI.as_view(),
        name="construction-categories-list"
    ),
]
