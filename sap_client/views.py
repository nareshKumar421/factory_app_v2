import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from company.permissions import HasCompanyContext
from .client import SAPClient
from .exceptions import SAPConnectionError, SAPDataError
from .serializers import POSerializer

logger = logging.getLogger(__name__)


class OpenPOListAPI(APIView):
    """
    Returns list of open POs for a supplier
    """
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def get(self, request):
        supplier_code = request.GET.get("supplier_code")
        if not supplier_code:
            return Response(
                {"detail": "supplier_code is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            client = SAPClient(company_code=request.company.company.code)
            po_list = client.get_open_pos(supplier_code)
        except SAPConnectionError as e:
            logger.error(f"SAP connection error in OpenPOListAPI: {e}")
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except SAPDataError as e:
            logger.error(f"SAP data error in OpenPOListAPI: {e}")
            return Response(
                {"detail": "Failed to retrieve PO data from SAP."},
                status=status.HTTP_502_BAD_GATEWAY
            )

        serializer = POSerializer(po_list, many=True)
        return Response(serializer.data)


class POItemListAPI(APIView):
    """
    Returns items for a specific PO
    """
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def get(self, request, po_number):
        try:
            client = SAPClient(company_code=request.company.company.code)
            pos = client.get_open_pos(supplier_code=None)
        except SAPConnectionError as e:
            logger.error(f"SAP connection error in POItemListAPI: {e}")
            return Response(
                {"detail": "SAP system is currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except SAPDataError as e:
            logger.error(f"SAP data error in POItemListAPI: {e}")
            return Response(
                {"detail": "Failed to retrieve PO data from SAP."},
                status=status.HTTP_502_BAD_GATEWAY
            )

        for po in pos:
            if po.po_number == po_number:
                return Response(
                    POSerializer(po).data
                )

        return Response(
            {"detail": "PO not found"},
            status=status.HTTP_404_NOT_FOUND
        )
