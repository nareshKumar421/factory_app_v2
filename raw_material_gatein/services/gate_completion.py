# raw_material_gatein/services/gate_completion.py

from gate_core.enums import GateEntryStatus
from gate_core.services import validate_status_transition
from gate_core.services import ensure_editable
from driver_management.models import VehicleEntry
from quality_control.services.rules import can_complete_gate


def complete_gate_entry(vehicle_entry: VehicleEntry):
    """
    Completes the gate entry after validating all rules.

    Gate entry can be completed when:
    1. Security check is submitted
    2. Weighment is completed
    3. At least one PO item exists
    4. All PO items have completed QC (ACCEPTED or REJECTED)
    """

    # 1. Ensure entry is editable
    ensure_editable(vehicle_entry)

    if vehicle_entry.status == GateEntryStatus.DRAFT:
        vehicle_entry.status = GateEntryStatus.IN_PROGRESS
        vehicle_entry.save(update_fields=["status"])

    # 2. Security check must exist and be submitted
    if not hasattr(vehicle_entry, "security_check"):
        raise ValueError("Security check is missing")

    if not vehicle_entry.security_check.is_submitted:
        raise ValueError("Security check not submitted")

    # 3. Weighment must exist
    if not hasattr(vehicle_entry, "weighment"):
        raise ValueError("Weighment not completed")

    # 4. At least one PO item must exist
    po_items = []
    for po in vehicle_entry.po_receipts.all():
        po_items.extend(list(po.items.all()))

    if not po_items:
        raise ValueError("No PO items received")

    # 5. Check if all PO items have completed QC (ACCEPTED or REJECTED)
    if not can_complete_gate(po_items):
        raise ValueError("QC is not completed for all items. All items must have inspection with ACCEPTED or REJECTED status.")

    # 6. Status transition validation
    # If status is QC_PENDING, first transition to QC_COMPLETED
    if vehicle_entry.status == GateEntryStatus.QC_PENDING:
        validate_status_transition(
            vehicle_entry.status,
            GateEntryStatus.QC_COMPLETED
        )
        vehicle_entry.status = GateEntryStatus.QC_COMPLETED
        vehicle_entry.save(update_fields=["status"])

    # Now transition to COMPLETED
    validate_status_transition(
        vehicle_entry.status,
        GateEntryStatus.COMPLETED
    )

    # 7. Lock & complete
    vehicle_entry.status = GateEntryStatus.COMPLETED
    vehicle_entry.is_locked = True
    vehicle_entry.save()

    return True
