# raw_material_gatein/services/gate_completion.py

from gate_core.enums import GateEntryStatus
from gate_core.services import validate_status_transition
from gate_core.services import ensure_editable
from driver_management.models import VehicleEntry

def complete_gate_entry(vehicle_entry: VehicleEntry):
    """
    Completes the gate entry after validating all rules.
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
        po_items.extend(po.items.all())

    if not po_items:
        raise ValueError("No PO items received")

    # 5. Entry must be in QC_COMPLETED status
    if vehicle_entry.status != GateEntryStatus.QC_COMPLETED:
        raise ValueError("QC is not completed for all items")

    # 6. Status transition validation
    validate_status_transition(
        vehicle_entry.status,
        GateEntryStatus.COMPLETED
    )

    # 7. Lock & complete
    vehicle_entry.status = GateEntryStatus.COMPLETED
    vehicle_entry.is_locked = True
    vehicle_entry.save()

    return True
