# gate_core/enums.py

from django.db import models


class GateEntryStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SECURITY_CHECK_DONE = "SECURITY_CHECK_DONE", "Security Check Done"
    ARRIVAL_SLIP_SUBMITTED = "ARRIVAL_SLIP_SUBMITTED", "Arrival Slip Submitted"
    ARRIVAL_SLIP_REJECTED = "ARRIVAL_SLIP_REJECTED", "Arrival Slip Rejected"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    QC_PENDING = "QC_PENDING", "QC Pending"
    QC_IN_REVIEW = "QC_IN_REVIEW", "QC In Review"
    QC_AWAITING_QAM = "QC_AWAITING_QAM", "Awaiting QAM Approval"
    QC_COMPLETED = "QC_COMPLETED", "QC Completed"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
