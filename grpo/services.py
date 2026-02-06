import logging
from typing import List, Dict, Any, Optional
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from gate_core.enums import GateEntryStatus
from driver_management.models import VehicleEntry
from raw_material_gatein.models import POReceipt, POItemReceipt
from quality_control.enums import InspectionStatus
from sap_client.client import SAPClient
from sap_client.exceptions import SAPConnectionError, SAPDataError, SAPValidationError

from .models import GRPOPosting, GRPOLinePosting, GRPOStatus

logger = logging.getLogger(__name__)


class GRPOService:
    """
    Service for handling GRPO operations.
    """

    def __init__(self, company_code: str):
        self.company_code = company_code

    def get_pending_grpo_entries(self) -> List[VehicleEntry]:
        """
        Get all completed gate entries that are ready for GRPO posting.
        Returns entries with status COMPLETED or QC_COMPLETED.
        """
        return VehicleEntry.objects.filter(
            company__code=self.company_code,
            entry_type="RAW_MATERIAL",
            status__in=[GateEntryStatus.COMPLETED, GateEntryStatus.QC_COMPLETED]
        ).prefetch_related(
            "po_receipts",
            "po_receipts__items",
            "grpo_postings"
        ).order_by("-entry_time")

    def get_grpo_preview_data(self, vehicle_entry_id: int) -> List[Dict[str, Any]]:
        """
        Get all data required for GRPO posting for a specific gate entry.
        Returns list of PO receipts with their items and QC status.
        """
        try:
            vehicle_entry = VehicleEntry.objects.prefetch_related(
                "po_receipts",
                "po_receipts__items",
                "po_receipts__items__arrival_slip",
                "po_receipts__items__arrival_slip__inspection",
                "grpo_postings"
            ).get(id=vehicle_entry_id)
        except VehicleEntry.DoesNotExist:
            raise ValueError(f"Vehicle entry {vehicle_entry_id} not found")

        is_ready = vehicle_entry.status in [
            GateEntryStatus.COMPLETED,
            GateEntryStatus.QC_COMPLETED
        ]

        result = []
        for po_receipt in vehicle_entry.po_receipts.all():
            # Check if GRPO already posted for this PO
            existing_grpo = vehicle_entry.grpo_postings.filter(
                po_receipt=po_receipt
            ).first()

            items_data = []
            for item in po_receipt.items.all():
                qc_status = self._get_item_qc_status(item)
                items_data.append({
                    "po_item_receipt_id": item.id,
                    "item_code": item.po_item_code,
                    "item_name": item.item_name,
                    "ordered_qty": item.ordered_qty,
                    "received_qty": item.received_qty,
                    "accepted_qty": item.accepted_qty,
                    "rejected_qty": item.rejected_qty,
                    "uom": item.uom,
                    "qc_status": qc_status
                })

            result.append({
                "vehicle_entry_id": vehicle_entry.id,
                "entry_no": vehicle_entry.entry_no,
                "entry_status": vehicle_entry.status,
                "is_ready_for_grpo": is_ready,
                "po_receipt_id": po_receipt.id,
                "po_number": po_receipt.po_number,
                "supplier_code": po_receipt.supplier_code,
                "supplier_name": po_receipt.supplier_name,
                "invoice_no": po_receipt.invoice_no or "",
                "invoice_date": po_receipt.invoice_date,
                "challan_no": po_receipt.challan_no or "",
                "items": items_data,
                "grpo_status": existing_grpo.status if existing_grpo else None,
                "sap_doc_num": existing_grpo.sap_doc_num if existing_grpo else None
            })

        return result

    def _get_item_qc_status(self, po_item_receipt: POItemReceipt) -> str:
        """Get QC status for a PO item receipt."""
        if not hasattr(po_item_receipt, "arrival_slip"):
            return "NO_ARRIVAL_SLIP"

        arrival_slip = po_item_receipt.arrival_slip
        if not arrival_slip.is_submitted:
            return "ARRIVAL_SLIP_PENDING"

        if not hasattr(arrival_slip, "inspection"):
            return "INSPECTION_PENDING"

        inspection = arrival_slip.inspection
        return inspection.final_status

    @transaction.atomic
    def post_grpo(
        self,
        vehicle_entry_id: int,
        po_receipt_id: int,
        user,
        warehouse_code: Optional[str] = None,
        comments: Optional[str] = None
    ) -> GRPOPosting:
        """
        Post GRPO to SAP for a specific PO receipt.
        Only posts accepted quantities.
        """
        # Get vehicle entry and PO receipt
        try:
            vehicle_entry = VehicleEntry.objects.get(id=vehicle_entry_id)
            po_receipt = POReceipt.objects.prefetch_related(
                "items",
                "items__arrival_slip",
                "items__arrival_slip__inspection"
            ).get(id=po_receipt_id, vehicle_entry=vehicle_entry)
        except VehicleEntry.DoesNotExist:
            raise ValueError(f"Vehicle entry {vehicle_entry_id} not found")
        except POReceipt.DoesNotExist:
            raise ValueError(f"PO receipt {po_receipt_id} not found for this vehicle entry")

        # Check if already posted
        existing = GRPOPosting.objects.filter(
            vehicle_entry=vehicle_entry,
            po_receipt=po_receipt,
            status=GRPOStatus.POSTED
        ).first()

        if existing:
            raise ValueError(
                f"GRPO already posted for PO {po_receipt.po_number}. "
                f"SAP Doc Num: {existing.sap_doc_num}"
            )

        # Validate gate entry status
        if vehicle_entry.status not in [
            GateEntryStatus.COMPLETED,
            GateEntryStatus.QC_COMPLETED
        ]:
            raise ValueError(
                f"Gate entry is not completed. Current status: {vehicle_entry.status}"
            )

        # Create or get GRPO posting record
        grpo_posting, created = GRPOPosting.objects.get_or_create(
            vehicle_entry=vehicle_entry,
            po_receipt=po_receipt,
            defaults={
                "status": GRPOStatus.PENDING,
                "posted_by": user
            }
        )

        # Build GRPO payload
        document_lines = []
        grpo_lines_data = []

        for item in po_receipt.items.all():
            # Only post accepted quantities
            if item.accepted_qty <= 0:
                continue

            line_data = {
                "ItemCode": item.po_item_code,
                "Quantity": str(item.accepted_qty),
            }

            if warehouse_code:
                line_data["WarehouseCode"] = warehouse_code

            # Note: BaseEntry, BaseLine, BaseType would need to come from
            # SAP PO data if linking to PO. For now, we create standalone GRPO.
            # TODO: Add PO linking support when DocEntry is available

            document_lines.append(line_data)
            grpo_lines_data.append({
                "po_item_receipt": item,
                "quantity_posted": item.accepted_qty
            })

        if not document_lines:
            grpo_posting.status = GRPOStatus.FAILED
            grpo_posting.error_message = "No accepted quantities to post"
            grpo_posting.save()
            raise ValueError("No accepted quantities to post for this PO")

        # Build full payload
        grpo_payload = {
            "CardCode": po_receipt.supplier_code,
            "DocumentLines": document_lines
        }

        if comments:
            grpo_payload["Comments"] = comments

        # Post to SAP
        try:
            sap_client = SAPClient(company_code=self.company_code)
            result = sap_client.create_grpo(grpo_payload)

            # Update GRPO posting with SAP response
            grpo_posting.sap_doc_entry = result.get("DocEntry")
            grpo_posting.sap_doc_num = result.get("DocNum")
            grpo_posting.sap_doc_total = Decimal(str(result.get("DocTotal", 0)))
            grpo_posting.status = GRPOStatus.POSTED
            grpo_posting.posted_at = timezone.now()
            grpo_posting.posted_by = user
            grpo_posting.save()

            # Create line posting records
            for line_data in grpo_lines_data:
                GRPOLinePosting.objects.create(
                    grpo_posting=grpo_posting,
                    po_item_receipt=line_data["po_item_receipt"],
                    quantity_posted=line_data["quantity_posted"]
                )

            logger.info(
                f"GRPO posted successfully for PO {po_receipt.po_number}. "
                f"SAP DocNum: {grpo_posting.sap_doc_num}"
            )

            return grpo_posting

        except SAPValidationError as e:
            grpo_posting.status = GRPOStatus.FAILED
            grpo_posting.error_message = str(e)
            grpo_posting.save()
            logger.error(f"SAP validation error posting GRPO: {e}")
            raise

        except SAPConnectionError as e:
            grpo_posting.status = GRPOStatus.FAILED
            grpo_posting.error_message = "SAP system unavailable"
            grpo_posting.save()
            logger.error(f"SAP connection error posting GRPO: {e}")
            raise

        except SAPDataError as e:
            grpo_posting.status = GRPOStatus.FAILED
            grpo_posting.error_message = str(e)
            grpo_posting.save()
            logger.error(f"SAP data error posting GRPO: {e}")
            raise

    def get_grpo_posting_history(
        self,
        vehicle_entry_id: Optional[int] = None
    ) -> List[GRPOPosting]:
        """Get GRPO posting history."""
        queryset = GRPOPosting.objects.select_related(
            "vehicle_entry",
            "po_receipt",
            "posted_by"
        ).prefetch_related("lines")

        if vehicle_entry_id:
            queryset = queryset.filter(vehicle_entry_id=vehicle_entry_id)

        return queryset.order_by("-created_at")
