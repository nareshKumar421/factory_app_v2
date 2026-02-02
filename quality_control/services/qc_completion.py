# quality_control/services/qc_completion.py

from gate_core.enums import GateEntryStatus
from gate_core.services import validate_status_transition
from ..enums import QCStatus


def check_and_mark_qc_completed(vehicle_entry):
    """
    Check if all QC inspections for a vehicle entry are completed (PASSED or FAILED).
    If so, transition the entry status to QC_COMPLETED.
    """
    if vehicle_entry.status != GateEntryStatus.QC_PENDING:
        return False

    po_items = []
    for po in vehicle_entry.po_receipts.all():
        po_items.extend(po.items.all())

    if not po_items:
        return False

    for item in po_items:
        if not hasattr(item, "qc_inspection"):
            return False
        if item.qc_inspection.qc_status == QCStatus.PENDING:
            return False

    validate_status_transition(
        vehicle_entry.status,
        GateEntryStatus.QC_COMPLETED
    )

    vehicle_entry.status = GateEntryStatus.QC_COMPLETED
    vehicle_entry.save(update_fields=["status"])

    return True
