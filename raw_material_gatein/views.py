import logging

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from company.permissions import HasCompanyContext
from driver_management.models import VehicleEntry
from gate_core.enums import GateEntryStatus
from sap_client.client import SAPClient
from sap_client.exceptions import SAPConnectionError, SAPDataError
from .models import POReceipt, POItemReceipt
from .serializers import POReceiveRequestSerializer, POItemReceiveSerializer
from .services import validate_received_quantity, complete_gate_entry
from .permissions import CanReceivePO, CanViewPOReceipt, CanCompleteRawMaterialEntry

logger = logging.getLogger(__name__)


class ReceivePOAPI(APIView):
    """
    Receive raw material PO items against a vehicle entry
    """
    permission_classes = [IsAuthenticated, HasCompanyContext, CanReceivePO]

    @transaction.atomic
    def post(self, request, gate_entry_id):
        entry = get_object_or_404(
            VehicleEntry,
            id=gate_entry_id,
            company=request.company.company
        )

        # Validate request payload
        request_serializer = POReceiveRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        validated_data = request_serializer.validated_data

        po_number = validated_data["po_number"]
        supplier_code = validated_data["supplier_code"]
        supplier_name = validated_data["supplier_name"]
        items_data = validated_data["items"]

        # Fetch SAP remaining quantities first (before creating any records)
        try:
            client = SAPClient(company_code=request.company.company.code)
            sap_pos = client.get_open_pos(supplier_code)
        except SAPConnectionError as e:
            logger.error(f"SAP connection error in ReceivePOAPI: {e}")
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except SAPDataError as e:
            logger.error(f"SAP data error in ReceivePOAPI: {e}")
            return Response(
                {"detail": "Failed to retrieve PO data from SAP."},
                status=status.HTTP_502_BAD_GATEWAY
            )

        # Create PO receipt header (after SAP validation succeeds)
        po_receipt = POReceipt.objects.create(
            vehicle_entry=entry,
            po_number=po_number,
            supplier_code=supplier_code,
            supplier_name=supplier_name,
            created_by=request.user
        )

        sap_items_map = {}
        for po in sap_pos:
            if po.po_number == po_number:
                for i in po.items:
                    sap_items_map[i.po_item_code] = i.remaining_qty

        for item_data in items_data:
            po_item_code = item_data["po_item_code"]
            received_qty = item_data["received_qty"]

            remaining_qty = sap_items_map.get(po_item_code)
            if remaining_qty is None:
                return Response(
                    {"detail": f"Invalid PO item {po_item_code}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                validate_received_quantity(
                    item_data["ordered_qty"],
                    remaining_qty,
                    received_qty
                )
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            POItemReceipt.objects.create(
                po_receipt=po_receipt,
                **item_data,
                created_by=request.user
            )

        # Update status after successful receipt
        if entry.status == GateEntryStatus.IN_PROGRESS:
            entry.status = GateEntryStatus.QC_PENDING
            entry.save(update_fields=["status"])

        return Response(
            {"message": "PO items received successfully"},
            status=status.HTTP_201_CREATED
        )


class GatePOListAPI(APIView):
    """
    List all PO receipts for a gate entry
    """
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewPOReceipt]

    def get(self, request, gate_entry_id):
        entry = get_object_or_404(
            VehicleEntry,
            id=gate_entry_id,
            company=request.company.company
        )

        response = []
        for po in entry.po_receipts.all():
            response.append({
                "id": po.id,
                "po_number": po.po_number,
                "supplier_code": po.supplier_code,
                "supplier_name": po.supplier_name,
                "items": [
                    {
                        "id": item.id,
                        "po_item_code": item.po_item_code,
                        "item_name": item.item_name,
                        "ordered_qty": item.ordered_qty,
                        "received_qty": item.received_qty,
                        "short_qty": item.short_qty,
                        "uom": item.uom,
                    }
                    for item in po.items.all()
                ]
            })

        return Response(response)


class CompleteGateEntryAPI(APIView):
    """
    Complete and lock a gate entry
    """
    permission_classes = [IsAuthenticated, HasCompanyContext, CanCompleteRawMaterialEntry]

    def post(self, request, gate_entry_id):
        entry = get_object_or_404(
            VehicleEntry,
            id=gate_entry_id,
            company=request.company.company
        )
        try:
            complete_gate_entry(entry)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Gate entry completed successfully"})

