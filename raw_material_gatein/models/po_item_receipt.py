# raw_material_gatein/models/po_item_receipt.py

from django.db import models
from gate_core.models import BaseModel
from ..models import POReceipt

class POItemReceipt(BaseModel):
    po_receipt = models.ForeignKey(
        POReceipt,
        on_delete=models.CASCADE,
        related_name="items"
    )

    po_item_code = models.CharField(max_length=50)
    item_name = models.CharField(max_length=200)

    ordered_qty = models.DecimalField(max_digits=12, decimal_places=3)
    received_qty = models.DecimalField(max_digits=12, decimal_places=3)

    accepted_qty = models.DecimalField(
        max_digits=12, decimal_places=3, default=0
    )
    rejected_qty = models.DecimalField(
        max_digits=12, decimal_places=3, default=0
    )

    short_qty = models.DecimalField(
        max_digits=12, decimal_places=3, editable=False
    )

    uom = models.CharField(max_length=20)

    class Meta:
        unique_together = ("po_receipt", "po_item_code")

    def save(self, *args, **kwargs):
        self.short_qty = self.ordered_qty - self.received_qty
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.po_item_code} - {self.item_name}"
