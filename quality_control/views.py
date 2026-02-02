from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import QCInspection
from .serializers import QCInspectionSerializer
from rest_framework.permissions import IsAuthenticated


class QCCreateUpdateAPI(APIView):
    """
    Create or update QC for a PO item
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, po_item_id):
        qc, _ = QCInspection.objects.get_or_create(
            po_item_receipt_id=po_item_id
        )

        serializer = QCInspectionSerializer(
            qc,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        # inspected_by should come from user
        serializer.save(
            inspected_by=request.user
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class QCDetailAPI(APIView):

    permission_classes = [IsAuthenticated]
    def get(self, request, po_item_id):
        try:
            qc = QCInspection.objects.get(
                po_item_receipt_id=po_item_id
            )
        except QCInspection.DoesNotExist:
            return Response(
                {"detail": "QC not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = QCInspectionSerializer(qc)
        return Response(serializer.data)
