import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from company.permissions import HasCompanyContext
from sap_client.exceptions import SAPConnectionError, SAPDataError, SAPValidationError

from .services import GRPOService
from .serializers import (
    GRPOPreviewSerializer,
    GRPOPostRequestSerializer,
    GRPOPostingSerializer,
    GRPOPostResponseSerializer
)
from .permissions import (
    CanViewPendingGRPO,
    CanPreviewGRPO,
    CanCreateGRPOPosting,
    CanViewGRPOHistory,
    CanViewGRPOPosting,
)

logger = logging.getLogger(__name__)


class PendingGRPOListAPI(APIView):
    """
    Returns list of completed gate entries pending GRPO posting.

    GET /api/grpo/pending/
    """
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewPendingGRPO]

    def get(self, request):
        service = GRPOService(company_code=request.company.company.code)
        entries = service.get_pending_grpo_entries()

        # Build response with summary for each entry
        result = []
        for entry in entries:
            po_receipts = entry.po_receipts.all()
            posted_count = entry.grpo_postings.filter(status="POSTED").count()
            total_count = po_receipts.count()
            pending_count = total_count - posted_count

            # Only include entries that have pending POs
            if pending_count > 0:
                result.append({
                    "vehicle_entry_id": entry.id,
                    "entry_no": entry.entry_no,
                    "status": entry.status,
                    "entry_time": entry.entry_time,
                    "total_po_count": total_count,
                    "posted_po_count": posted_count,
                    "pending_po_count": pending_count,
                    "is_fully_posted": False
                })

        return Response(result)


class GRPOPreviewAPI(APIView):
    """
    Returns all data required for GRPO posting for a specific gate entry.
    Shows PO details, items, QC status, and accepted quantities.

    GET /api/grpo/preview/<vehicle_entry_id>/
    """
    permission_classes = [IsAuthenticated, HasCompanyContext, CanPreviewGRPO]

    def get(self, request, vehicle_entry_id):
        service = GRPOService(company_code=request.company.company.code)

        try:
            preview_data = service.get_grpo_preview_data(vehicle_entry_id)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = GRPOPreviewSerializer(preview_data, many=True)
        return Response(serializer.data)


class PostGRPOAPI(APIView):
    """
    Post GRPO to SAP for a specific PO receipt.
    Includes PO linking (BaseEntry/BaseLine/BaseType), new line-level fields,
    vendor reference, extra charges, and structured comments.

    POST /api/grpo/post/
    """
    permission_classes = [IsAuthenticated, HasCompanyContext, CanCreateGRPOPosting]

    def post(self, request):
        serializer = GRPOPostRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"detail": "Invalid request data", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = GRPOService(company_code=request.company.company.code)

        try:
            grpo_posting = service.post_grpo(
                vehicle_entry_id=serializer.validated_data["vehicle_entry_id"],
                po_receipt_id=serializer.validated_data["po_receipt_id"],
                user=request.user,
                items=serializer.validated_data["items"],
                branch_id=serializer.validated_data["branch_id"],
                warehouse_code=serializer.validated_data.get("warehouse_code"),
                comments=serializer.validated_data.get("comments"),
                vendor_ref=serializer.validated_data.get("vendor_ref"),
                extra_charges=serializer.validated_data.get("extra_charges"),
            )

            response_data = {
                "success": True,
                "grpo_posting_id": grpo_posting.id,
                "sap_doc_entry": grpo_posting.sap_doc_entry,
                "sap_doc_num": grpo_posting.sap_doc_num,
                "sap_doc_total": grpo_posting.sap_doc_total,
                "message": f"GRPO posted successfully. SAP Doc Num: {grpo_posting.sap_doc_num}"
            }

            return Response(
                GRPOPostResponseSerializer(response_data).data,
                status=status.HTTP_201_CREATED
            )

        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except SAPValidationError as e:
            return Response(
                {"detail": f"SAP validation error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        except SAPConnectionError:
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        except SAPDataError as e:
            return Response(
                {"detail": f"SAP error: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY
            )


class GRPOPostingHistoryAPI(APIView):
    """
    Returns GRPO posting history.

    GET /api/grpo/history/
    GET /api/grpo/history/?vehicle_entry_id=123
    """
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewGRPOHistory]

    def get(self, request):
        vehicle_entry_id = request.GET.get("vehicle_entry_id")

        service = GRPOService(company_code=request.company.company.code)
        postings = service.get_grpo_posting_history(
            vehicle_entry_id=int(vehicle_entry_id) if vehicle_entry_id else None
        )

        serializer = GRPOPostingSerializer(postings, many=True)
        return Response(serializer.data)


class GRPOPostingDetailAPI(APIView):
    """
    Returns details of a specific GRPO posting.

    GET /api/grpo/<posting_id>/
    """
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewGRPOPosting]

    def get(self, request, posting_id):
        from .models import GRPOPosting

        try:
            posting = GRPOPosting.objects.select_related(
                "vehicle_entry",
                "po_receipt",
                "posted_by"
            ).prefetch_related("lines").get(id=posting_id)
        except GRPOPosting.DoesNotExist:
            return Response(
                {"detail": "GRPO posting not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = GRPOPostingSerializer(posting)
        return Response(serializer.data)
