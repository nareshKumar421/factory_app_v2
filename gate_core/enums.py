# gate_core/enums.py

from django.db import models

class GateEntryStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    QC_PENDING = "QC_PENDING", "QC Pending"
    QC_COMPLETED = "QC_COMPLETED", "QC Completed"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
