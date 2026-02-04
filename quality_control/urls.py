from django.urls import path
from .views import (
    # Legacy QC APIs
    QCCreateUpdateAPI,
    QCDetailAPI,
    # Material Type APIs
    MaterialTypeListCreateAPI,
    MaterialTypeDetailAPI,
    # QC Parameter Master APIs
    QCParameterListCreateAPI,
    QCParameterDetailAPI,
    # Material Arrival Slip APIs
    ArrivalSlipCreateUpdateAPI,
    ArrivalSlipSubmitAPI,
    # Raw Material Inspection APIs
    InspectionPendingListAPI,
    InspectionCreateUpdateAPI,
    InspectionParameterResultsAPI,
    InspectionSubmitAPI,
    # Approval APIs
    InspectionApproveChemistAPI,
    InspectionApproveQAMAPI,
    InspectionRejectAPI,
)

urlpatterns = [
    # ==================== Legacy QC APIs ====================
    path(
        "po-items/<int:po_item_id>/qc/",
        QCCreateUpdateAPI.as_view()
    ),
    path(
        "po-items/<int:po_item_id>/qc/view/",
        QCDetailAPI.as_view()
    ),

    # ==================== Material Type APIs ====================
    path(
        "material-types/",
        MaterialTypeListCreateAPI.as_view(),
        name="material-type-list-create"
    ),
    path(
        "material-types/<int:material_type_id>/",
        MaterialTypeDetailAPI.as_view(),
        name="material-type-detail"
    ),

    # ==================== QC Parameter Master APIs ====================
    path(
        "material-types/<int:material_type_id>/parameters/",
        QCParameterListCreateAPI.as_view(),
        name="qc-parameter-list-create"
    ),
    path(
        "parameters/<int:parameter_id>/",
        QCParameterDetailAPI.as_view(),
        name="qc-parameter-detail"
    ),

    # ==================== Material Arrival Slip APIs ====================
    path(
        "gate-entries/<int:gate_entry_id>/arrival-slip/",
        ArrivalSlipCreateUpdateAPI.as_view(),
        name="arrival-slip-create-update"
    ),
    path(
        "arrival-slips/<int:slip_id>/submit/",
        ArrivalSlipSubmitAPI.as_view(),
        name="arrival-slip-submit"
    ),

    # ==================== Raw Material Inspection APIs ====================
    path(
        "inspections/pending/",
        InspectionPendingListAPI.as_view(),
        name="inspection-pending-list"
    ),
    path(
        "po-items/<int:po_item_id>/inspection/",
        InspectionCreateUpdateAPI.as_view(),
        name="inspection-create-update"
    ),
    path(
        "inspections/<int:inspection_id>/parameters/",
        InspectionParameterResultsAPI.as_view(),
        name="inspection-parameters"
    ),
    path(
        "inspections/<int:inspection_id>/submit/",
        InspectionSubmitAPI.as_view(),
        name="inspection-submit"
    ),

    # ==================== Approval APIs ====================
    path(
        "inspections/<int:inspection_id>/approve/chemist/",
        InspectionApproveChemistAPI.as_view(),
        name="inspection-approve-chemist"
    ),
    path(
        "inspections/<int:inspection_id>/approve/qam/",
        InspectionApproveQAMAPI.as_view(),
        name="inspection-approve-qam"
    ),
    path(
        "inspections/<int:inspection_id>/reject/",
        InspectionRejectAPI.as_view(),
        name="inspection-reject"
    ),
]
