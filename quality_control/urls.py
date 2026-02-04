# quality_control/urls.py

from django.urls import path
from .views import (
    # Material Type APIs
    MaterialTypeListCreateAPI,
    MaterialTypeDetailAPI,
    # QC Parameter Master APIs
    QCParameterListCreateAPI,
    QCParameterDetailAPI,
    # Material Arrival Slip APIs
    ArrivalSlipListAPI,
    ArrivalSlipCreateUpdateAPI,
    ArrivalSlipDetailAPI,
    ArrivalSlipSubmitAPI,
    # Raw Material Inspection APIs
    InspectionPendingListAPI,
    InspectionCreateUpdateAPI,
    InspectionDetailAPI,
    InspectionParameterResultsAPI,
    InspectionSubmitAPI,
    # Approval APIs
    InspectionApproveChemistAPI,
    InspectionApproveQAMAPI,
    InspectionRejectAPI,
)

urlpatterns = [
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
    # List all arrival slips
    path(
        "arrival-slips/",
        ArrivalSlipListAPI.as_view(),
        name="arrival-slip-list"
    ),
    # Create/update arrival slip for a PO item
    path(
        "po-items/<int:po_item_id>/arrival-slip/",
        ArrivalSlipCreateUpdateAPI.as_view(),
        name="arrival-slip-create-update"
    ),
    # Get arrival slip by ID
    path(
        "arrival-slips/<int:slip_id>/",
        ArrivalSlipDetailAPI.as_view(),
        name="arrival-slip-detail"
    ),
    # Submit arrival slip to QA
    path(
        "arrival-slips/<int:slip_id>/submit/",
        ArrivalSlipSubmitAPI.as_view(),
        name="arrival-slip-submit"
    ),

    # ==================== Raw Material Inspection APIs ====================
    # List pending arrival slips for QA inspection
    path(
        "inspections/pending/",
        InspectionPendingListAPI.as_view(),
        name="inspection-pending-list"
    ),
    # Create/update inspection for an arrival slip
    path(
        "arrival-slips/<int:slip_id>/inspection/",
        InspectionCreateUpdateAPI.as_view(),
        name="inspection-create-update"
    ),
    # Get inspection by ID
    path(
        "inspections/<int:inspection_id>/",
        InspectionDetailAPI.as_view(),
        name="inspection-detail"
    ),
    # Update parameter results
    path(
        "inspections/<int:inspection_id>/parameters/",
        InspectionParameterResultsAPI.as_view(),
        name="inspection-parameters"
    ),
    # Submit inspection for approval
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
