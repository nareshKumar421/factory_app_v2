import logging

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from driver_management.models import VehicleEntry
from .models import MaintenanceGateEntry, MaintenanceType
from .serializers import MaintenanceGateEntrySerializer, MaintenanceTypeSerializer
from .services import complete_maintenance_gate_entry
from company.permissions import HasCompanyContext
from .permissions import (
    CanCreateMaintenanceEntry,
    CanViewMaintenanceEntry,
    CanEditMaintenanceEntry,
    CanCompleteMaintenanceEntry,
    CanViewMaintenanceType,
)

logger = logging.getLogger(__name__)


class MaintenanceGateEntryCreateAPI(APIView):
    """
    Create/Read Maintenance & Repair Material gate entry.
    GET: Retrieve existing maintenance entry for a gate entry.
    POST: Create new maintenance entry for a gate entry.
    """
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), HasCompanyContext(), CanCreateMaintenanceEntry()]
        return [IsAuthenticated(), HasCompanyContext(), CanViewMaintenanceEntry()]

    def get(self, request, gate_entry_id):
        """Get maintenance entry for a specific vehicle entry"""
        entry = get_object_or_404(
            VehicleEntry,
            id=gate_entry_id,
            company=request.company.company
        )

        if hasattr(entry, "maintenance_entry"):
            serializer = MaintenanceGateEntrySerializer(entry.maintenance_entry)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "Maintenance entry does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

    @transaction.atomic
    def post(self, request, gate_entry_id):
        """Create maintenance entry for a specific vehicle entry"""
        entry = get_object_or_404(
            VehicleEntry,
            id=gate_entry_id,
            company=request.company.company
        )

        # Validate entry type
        if entry.entry_type != "MAINTENANCE":
            logger.warning(
                f"Invalid entry type {entry.entry_type} for maintenance creation. "
                f"Gate entry ID: {gate_entry_id}, User: {request.user}"
            )
            return Response(
                {"detail": "Invalid entry type. Expected MAINTENANCE."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if locked
        if entry.is_locked:
            return Response(
                {"detail": "Gate entry is locked"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if already exists
        if hasattr(entry, "maintenance_entry"):
            return Response(
                {"detail": "Maintenance entry already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = MaintenanceGateEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        maintenance_entry = serializer.save(
            vehicle_entry=entry,
            created_by=request.user
        )

        logger.info(
            f"Maintenance entry created. ID: {maintenance_entry.id}, "
            f"Gate entry: {gate_entry_id}, User: {request.user}"
        )

        return Response(
            {
                "message": "Maintenance gate entry created",
                "id": maintenance_entry.id,
                "work_order_number": maintenance_entry.work_order_number
            },
            status=status.HTTP_201_CREATED
        )


class MaintenanceGateEntryUpdateAPI(APIView):
    """
    Update existing Maintenance & Repair Material gate entry.
    PUT/PATCH: Update maintenance entry.
    """
    permission_classes = [IsAuthenticated, HasCompanyContext, CanEditMaintenanceEntry]

    @transaction.atomic
    def put(self, request, gate_entry_id):
        """Update maintenance entry for a specific vehicle entry"""
        entry = get_object_or_404(
            VehicleEntry,
            id=gate_entry_id,
            company=request.company.company
        )

        if entry.is_locked:
            return Response(
                {"detail": "Gate entry is locked"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not hasattr(entry, "maintenance_entry"):
            return Response(
                {"detail": "Maintenance entry does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MaintenanceGateEntrySerializer(
            entry.maintenance_entry,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        logger.info(
            f"Maintenance entry updated. Gate entry: {gate_entry_id}, "
            f"User: {request.user}"
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class MaintenanceGateCompleteAPI(APIView):
    """
    Final completion for Maintenance & Repair Material gate entry.
    """
    permission_classes = [IsAuthenticated, HasCompanyContext, CanCompleteMaintenanceEntry]

    def post(self, request, gate_entry_id):
        entry = get_object_or_404(
            VehicleEntry,
            id=gate_entry_id,
            company=request.company.company
        )

        try:
            complete_maintenance_gate_entry(entry)
            logger.info(
                f"Maintenance entry completed. Gate entry: {gate_entry_id}, "
                f"User: {request.user}"
            )
        except ValidationError as e:
            logger.warning(
                f"Maintenance completion failed. Gate entry: {gate_entry_id}, "
                f"Error: {str(e)}, User: {request.user}"
            )
            return Response(
                {"detail": str(e.detail) if hasattr(e, 'detail') else str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "Maintenance gate entry completed successfully"},
            status=status.HTTP_200_OK
        )


class MaintenanceTypeListAPI(APIView):
    """
    List all active maintenance types for dropdown.
    """
    permission_classes = [IsAuthenticated, CanViewMaintenanceType]

    def get(self, request):
        types = MaintenanceType.objects.filter(is_active=True)
        serializer = MaintenanceTypeSerializer(types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
