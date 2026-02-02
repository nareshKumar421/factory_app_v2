# quality_control/services/rules.py

from ..enums import QCStatus

def can_complete_gate(qc_list):
    """
    Gate can complete only if:
    - No QC item is PENDING
    """
    for qc in qc_list:
        if qc.qc_status == QCStatus.PENDING:
            return False
    return True
