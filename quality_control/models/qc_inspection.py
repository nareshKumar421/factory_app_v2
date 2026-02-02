# quality_control/models/qc_inspection.py

from django.db import models
from gate_core.models import BaseModel
from raw_material_gatein.models import POItemReceipt
from ..enums import QCStatus
from ..services.qc_completion import check_and_mark_qc_completed
from django.conf import settings

User = settings.AUTH_USER_MODEL

class QCInspection(BaseModel):

    po_item_receipt = models.OneToOneField(
        POItemReceipt,
        on_delete=models.CASCADE,
        related_name="qc_inspection"
    )

    qc_status = models.CharField(
        max_length=20,
        choices=QCStatus.choices,
        default=QCStatus.PENDING
    )

    sample_collected = models.BooleanField(default=False)

    batch_no = models.CharField(max_length=50, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    inspected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qc_inspections"
    )
    inspection_time = models.DateTimeField(auto_now_add=True)

    remarks = models.TextField(blank=True)

    is_locked = models.BooleanField(default=False)

    def __str__(self):
        return f"QC - {self.po_item_receipt.po_item_code}"
    

    def save(self, *args, **kwargs):
        if self.pk:
            old = QCInspection.objects.get(pk=self.pk)
            if old.is_locked:
                raise ValueError("QC is locked and cannot be modified")

        if self.qc_status in [QCStatus.PASSED, QCStatus.FAILED]:
            self.is_locked = True

        super().save(*args, **kwargs)

        if self.qc_status in [QCStatus.PASSED, QCStatus.FAILED]:
            vehicle_entry = self.po_item_receipt.po_receipt.vehicle_entry
            check_and_mark_qc_completed(vehicle_entry)

