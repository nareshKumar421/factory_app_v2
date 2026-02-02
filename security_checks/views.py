from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from company.permissions import HasCompanyContext
from driver_management.models import VehicleEntry
from gate_core.enums import GateEntryStatus
from .models import SecurityCheck
from .serializers import SecurityCheckSerializer


class SecurityCheckCreateUpdateAPI(APIView):
    """
    Create or update security check for a gate entry
    """
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def post(self, request, gate_entry_id):
        entry = get_object_or_404(
            VehicleEntry,
            id=gate_entry_id,
            company=request.company.company
        )

        if entry.status == GateEntryStatus.DRAFT:
            entry.status = GateEntryStatus.IN_PROGRESS
            entry.save(update_fields=["status"])

        security_check, _ = SecurityCheck.objects.get_or_create(
            vehicle_entry=entry
        )

        serializer = SecurityCheckSerializer(
            security_check,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user,updated_by=request.user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    

class SecurityCheckDetailAPI(APIView):
    """
    Get security check details for a gate entry
    """
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def get(self, request, gate_entry_id):
        entry = get_object_or_404(
            VehicleEntry,
            id=gate_entry_id,
            company=request.company.company
        )

        if not hasattr(entry, "security_check"):
            return Response(
                {"detail": "Security check not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SecurityCheckSerializer(entry.security_check)
        return Response(serializer.data)


class SubmitSecurityCheckAPI(APIView):
    """
    Final submission locks security check forever
    """
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def post(self, request, security_id):
        sc = get_object_or_404(
            SecurityCheck,
            id=security_id,
            vehicle_entry__company=request.company.company
        )

        if sc.is_submitted:
            return Response(
                {"detail": "Security check already submitted"},
                status=status.HTTP_400_BAD_REQUEST
            )

        sc.is_submitted = True
        sc.save()

        return Response(
            {"message": "Security check submitted successfully"},
            status=status.HTTP_200_OK
        )

