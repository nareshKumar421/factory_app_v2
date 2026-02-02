# gate_core/services/status_guard.py

from ..enums import GateEntryStatus

ALLOWED_TRANSITIONS = {
    GateEntryStatus.DRAFT: [GateEntryStatus.IN_PROGRESS],
    GateEntryStatus.IN_PROGRESS: [GateEntryStatus.QC_PENDING],
    GateEntryStatus.QC_PENDING: [GateEntryStatus.QC_COMPLETED],
    GateEntryStatus.QC_COMPLETED: [GateEntryStatus.COMPLETED],
}

def validate_status_transition(old_status, new_status):
    allowed = ALLOWED_TRANSITIONS.get(old_status, [])
    if new_status not in allowed:
        raise ValueError(
            f"Invalid status transition: {old_status} → {new_status}"
        )
