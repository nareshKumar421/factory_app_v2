from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from company.permissions import HasCompanyContext
from driver_management.models import VehicleEntry
from .models import Weighment
from .serializers import WeighmentSerializer


class WeighmentCreateUpdateAPI(APIView):
    """
    Create or update weighment for a gate entry
    """
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def post(self, request, gate_entry_id):
        entry = get_object_or_404(
            VehicleEntry,
            id=gate_entry_id,
            company=request.company.company
        )

        weighment, _ = Weighment.objects.get_or_create(
            vehicle_entry=entry
        )

        serializer = WeighmentSerializer(
            weighment,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user, updated_by=request.user)

        return Response(
            {
                "id": weighment.id,
                "gross_weight": weighment.gross_weight,
                "tare_weight": weighment.tare_weight,
                "net_weight": weighment.net_weight,
            },
            status=status.HTTP_200_OK
        )


class WeighmentDetailAPI(APIView):
    """
    Get weighment details for a gate entry
    """
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def get(self, request, gate_entry_id):
        entry = get_object_or_404(
            VehicleEntry,
            id=gate_entry_id,
            company=request.company.company
        )

        if not hasattr(entry, "weighment"):
            return Response(
                {"detail": "Weighment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = WeighmentSerializer(entry.weighment)
        return Response(serializer.data)
