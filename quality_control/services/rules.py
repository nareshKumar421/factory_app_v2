# quality_control/services/rules.py

from ..enums import InspectionStatus, InspectionWorkflowStatus


def can_complete_gate(po_items):
    """
    Gate can complete only if all PO items have completed QC inspection.

    A PO item's QC is complete when:
    1. It has an arrival slip
    2. The arrival slip has an inspection
    3. The inspection has final_status of ACCEPTED or REJECTED (not PENDING or HOLD)

    Args:
        po_items: List of POItemReceipt objects

    Returns:
        bool: True if all items have completed QC, False otherwise
    """
    if not po_items:
        return False

    for item in po_items:
        # Check if arrival slip exists
        if not hasattr(item, 'arrival_slip') or item.arrival_slip is None:
            return False

        arrival_slip = item.arrival_slip

        # Check if inspection exists
        if not hasattr(arrival_slip, 'inspection') or arrival_slip.inspection is None:
            return False

        inspection = arrival_slip.inspection

        # Check if inspection is completed (ACCEPTED or REJECTED)
        if inspection.final_status not in [InspectionStatus.ACCEPTED, InspectionStatus.REJECTED]:
            return False

    return True


def check_and_mark_qc_completed(vehicle_entry):
    """
    Check if all QC inspections for a vehicle entry are completed.
    If so, transition the entry status to QC_COMPLETED.

    This replaces the old qc_completion.py service.
    """
    from gate_core.enums import GateEntryStatus
    from gate_core.services import validate_status_transition

    if vehicle_entry.status != GateEntryStatus.QC_PENDING:
        return False

    # Collect all PO items
    po_items = []
    for po in vehicle_entry.po_receipts.all():
        po_items.extend(list(po.items.all()))

    if not po_items:
        return False

    # Check if all items have completed QC
    if not can_complete_gate(po_items):
        return False

    # Validate and perform status transition
    validate_status_transition(
        vehicle_entry.status,
        GateEntryStatus.QC_COMPLETED
    )

    vehicle_entry.status = GateEntryStatus.QC_COMPLETED
    vehicle_entry.save(update_fields=["status"])

    return True
