from django.db import models
from django.conf import settings
from driver_management.models import VehicleEntry
from raw_material_gatein.models import POReceipt, POItemReceipt


class GRPOStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    POSTED = "POSTED", "Posted to SAP"
    FAILED = "FAILED", "Failed"
    PARTIALLY_POSTED = "PARTIALLY_POSTED", "Partially Posted"


class GRPOPosting(models.Model):
    """
    Tracks GRPO postings to SAP for completed gate entries.
    One gate entry can have multiple GRPO postings (one per PO).
    """
    vehicle_entry = models.ForeignKey(
        VehicleEntry,
        on_delete=models.PROTECT,
        related_name="grpo_postings"
    )

    po_receipt = models.ForeignKey(
        POReceipt,
        on_delete=models.PROTECT,
        related_name="grpo_postings"
    )

    # SAP Response Fields
    sap_doc_entry = models.IntegerField(null=True, blank=True, help_text="SAP DocEntry")
    sap_doc_num = models.IntegerField(null=True, blank=True, help_text="SAP DocNum")
    sap_doc_total = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=GRPOStatus.choices,
        default=GRPOStatus.PENDING
    )

    error_message = models.TextField(blank=True, null=True)

    # Audit fields
    posted_at = models.DateTimeField(null=True, blank=True)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grpo_postings"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("vehicle_entry", "po_receipt")
        ordering = ["-created_at"]
        permissions = [
            ("can_view_pending_grpo", "Can view pending grpo entries"),
            ("can_preview_grpo", "Can preview grpo data"),
            ("can_view_grpo_history", "Can view GRPO posting history"),
        ]

    def __str__(self):
        return f"GRPO for {self.po_receipt.po_number} - {self.status}"


class GRPOLinePosting(models.Model):
    """
    Tracks individual line items posted in a GRPO.
    Links to POItemReceipt for traceability.
    """
    grpo_posting = models.ForeignKey(
        GRPOPosting,
        on_delete=models.CASCADE,
        related_name="lines"
    )

    po_item_receipt = models.ForeignKey(
        POItemReceipt,
        on_delete=models.PROTECT,
        related_name="grpo_lines"
    )

    # Quantities posted
    quantity_posted = models.DecimalField(max_digits=12, decimal_places=3)

    # SAP line details
    base_entry = models.IntegerField(null=True, blank=True, help_text="PO DocEntry in SAP")
    base_line = models.IntegerField(null=True, blank=True, help_text="PO Line Number in SAP")
    

    def __str__(self):
        return f"{self.po_item_receipt.item_name} - {self.quantity_posted}"
