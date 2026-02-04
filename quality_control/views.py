from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from company.permissions import HasCompanyContext
from driver_management.models import VehicleEntry
from raw_material_gatein.models import POItemReceipt
from gate_core.enums import GateEntryStatus

from .models import (
    QCInspection,
    MaterialType,
    QCParameterMaster,
    MaterialArrivalSlip,
    RawMaterialInspection,
    InspectionParameterResult,
)
from .serializers import (
    QCInspectionSerializer,
    MaterialTypeSerializer,
    MaterialTypeCreateSerializer,
    QCParameterMasterSerializer,
    QCParameterMasterCreateSerializer,
    MaterialArrivalSlipSerializer,
    MaterialArrivalSlipCreateSerializer,
    RawMaterialInspectionSerializer,
    RawMaterialInspectionCreateSerializer,
    InspectionParameterResultSerializer,
    ApprovalSerializer,
    ParameterResultBulkUpdateSerializer,
)
from .permissions import (
    CanManageArrivalSlip,
    CanSubmitArrivalSlip,
    CanViewArrivalSlip,
    CanManageInspection,
    CanSubmitInspection,
    CanViewInspection,
    CanApproveAsChemist,
    CanApproveAsQAM,
    CanRejectInspection,
    CanManageMaterialTypes,
    CanManageQCParameters,
)
from .enums import (
    ArrivalSlipStatus,
    InspectionStatus,
    InspectionWorkflowStatus,
)


# ==================== Legacy QC APIs (Backward Compatibility) ====================

class QCCreateUpdateAPI(APIView):
    """
    Create or update QC for a PO item (Legacy API)
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

        serializer.save(
            inspected_by=request.user
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class QCDetailAPI(APIView):
    """Legacy QC detail API"""
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


# ==================== Material Type APIs ====================

class MaterialTypeListCreateAPI(APIView):
    """List and create material types"""
    permission_classes = [IsAuthenticated, HasCompanyContext, CanManageMaterialTypes]

    def get(self, request):
        material_types = MaterialType.objects.filter(
            company=request.company.company,
            is_active=True
        )
        serializer = MaterialTypeSerializer(material_types, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MaterialTypeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        material_type = MaterialType.objects.create(
            company=request.company.company,
            created_by=request.user,
            **serializer.validated_data
        )
        return Response(
            MaterialTypeSerializer(material_type).data,
            status=status.HTTP_201_CREATED
        )


class MaterialTypeDetailAPI(APIView):
    """Get, update, delete material type"""
    permission_classes = [IsAuthenticated, HasCompanyContext, CanManageMaterialTypes]

    def get(self, request, material_type_id):
        material_type = get_object_or_404(
            MaterialType,
            id=material_type_id,
            company=request.company.company
        )
        serializer = MaterialTypeSerializer(material_type)
        return Response(serializer.data)

    def put(self, request, material_type_id):
        material_type = get_object_or_404(
            MaterialType,
            id=material_type_id,
            company=request.company.company
        )
        serializer = MaterialTypeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for key, value in serializer.validated_data.items():
            setattr(material_type, key, value)
        material_type.updated_by = request.user
        material_type.save()

        return Response(MaterialTypeSerializer(material_type).data)

    def delete(self, request, material_type_id):
        material_type = get_object_or_404(
            MaterialType,
            id=material_type_id,
            company=request.company.company
        )
        material_type.is_active = False
        material_type.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==================== QC Parameter Master APIs ====================

class QCParameterListCreateAPI(APIView):
    """List and create QC parameters for a material type"""
    permission_classes = [IsAuthenticated, HasCompanyContext, CanManageQCParameters]

    def get(self, request, material_type_id):
        material_type = get_object_or_404(
            MaterialType,
            id=material_type_id,
            company=request.company.company
        )
        parameters = QCParameterMaster.objects.filter(
            material_type=material_type,
            is_active=True
        )
        serializer = QCParameterMasterSerializer(parameters, many=True)
        return Response(serializer.data)

    def post(self, request, material_type_id):
        material_type = get_object_or_404(
            MaterialType,
            id=material_type_id,
            company=request.company.company
        )
        serializer = QCParameterMasterCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        parameter = QCParameterMaster.objects.create(
            material_type=material_type,
            created_by=request.user,
            **serializer.validated_data
        )
        return Response(
            QCParameterMasterSerializer(parameter).data,
            status=status.HTTP_201_CREATED
        )


class QCParameterDetailAPI(APIView):
    """Get, update, delete QC parameter"""
    permission_classes = [IsAuthenticated, HasCompanyContext, CanManageQCParameters]

    def get(self, request, parameter_id):
        parameter = get_object_or_404(
            QCParameterMaster,
            id=parameter_id,
            material_type__company=request.company.company
        )
        serializer = QCParameterMasterSerializer(parameter)
        return Response(serializer.data)

    def put(self, request, parameter_id):
        parameter = get_object_or_404(
            QCParameterMaster,
            id=parameter_id,
            material_type__company=request.company.company
        )
        serializer = QCParameterMasterCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for key, value in serializer.validated_data.items():
            setattr(parameter, key, value)
        parameter.updated_by = request.user
        parameter.save()

        return Response(QCParameterMasterSerializer(parameter).data)

    def delete(self, request, parameter_id):
        parameter = get_object_or_404(
            QCParameterMaster,
            id=parameter_id,
            material_type__company=request.company.company
        )
        parameter.is_active = False
        parameter.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==================== Material Arrival Slip APIs ====================

class ArrivalSlipCreateUpdateAPI(APIView):
    """Create or update arrival slip for a gate entry"""
    permission_classes = [IsAuthenticated, HasCompanyContext, CanManageArrivalSlip]

    def get(self, request, gate_entry_id):
        entry = get_object_or_404(
            VehicleEntry,
            id=gate_entry_id,
            company=request.company.company
        )
        try:
            slip = entry.arrival_slip
            serializer = MaterialArrivalSlipSerializer(slip)
            return Response(serializer.data)
        except MaterialArrivalSlip.DoesNotExist:
            return Response(
                {"detail": "Arrival slip not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, gate_entry_id):
        entry = get_object_or_404(
            VehicleEntry,
            id=gate_entry_id,
            company=request.company.company
        )

        serializer = MaterialArrivalSlipCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        slip, created = MaterialArrivalSlip.objects.get_or_create(
            vehicle_entry=entry,
            defaults={
                "created_by": request.user,
                **serializer.validated_data
            }
        )

        if not created:
            # Check if already submitted and not rejected
            if slip.is_submitted and slip.status != ArrivalSlipStatus.REJECTED:
                return Response(
                    {"detail": "Arrival slip already submitted"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update existing slip
            for key, value in serializer.validated_data.items():
                setattr(slip, key, value)
            slip.updated_by = request.user

            # If was rejected, reset to draft
            if slip.status == ArrivalSlipStatus.REJECTED:
                slip.status = ArrivalSlipStatus.DRAFT
                slip.is_submitted = False

            slip.save()

        return Response(
            MaterialArrivalSlipSerializer(slip).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class ArrivalSlipSubmitAPI(APIView):
    """Submit arrival slip to QA"""
    permission_classes = [IsAuthenticated, HasCompanyContext, CanSubmitArrivalSlip]

    def post(self, request, slip_id):
        slip = get_object_or_404(
            MaterialArrivalSlip,
            id=slip_id,
            vehicle_entry__company=request.company.company
        )

        if slip.is_submitted and slip.status == ArrivalSlipStatus.SUBMITTED:
            return Response(
                {"detail": "Already submitted"},
                status=status.HTTP_400_BAD_REQUEST
            )

        slip.submit_to_qa(request.user)

        # Update vehicle entry status
        entry = slip.vehicle_entry
        entry.status = GateEntryStatus.ARRIVAL_SLIP_SUBMITTED
        entry.save(update_fields=["status"])

        return Response(
            MaterialArrivalSlipSerializer(slip).data,
            status=status.HTTP_200_OK
        )


# ==================== Raw Material Inspection APIs ====================

class InspectionPendingListAPI(APIView):
    """List inspections pending for QA"""
    permission_classes = [IsAuthenticated, HasCompanyContext, CanViewInspection]

    def get(self, request):
        # Get all vehicle entries with submitted arrival slips
        entries = VehicleEntry.objects.filter(
            company=request.company.company,
            status__in=[
                GateEntryStatus.ARRIVAL_SLIP_SUBMITTED,
                GateEntryStatus.IN_PROGRESS,
                GateEntryStatus.QC_PENDING,
            ]
        ).select_related("arrival_slip")

        result = []
        for entry in entries:
            if hasattr(entry, "arrival_slip"):
                result.append({
                    "gate_entry_id": entry.id,
                    "entry_no": entry.entry_no,
                    "status": entry.status,
                    "arrival_slip": MaterialArrivalSlipSerializer(entry.arrival_slip).data
                })

        return Response(result)


class InspectionCreateUpdateAPI(APIView):
    """Create or update inspection for a PO item"""
    permission_classes = [IsAuthenticated, HasCompanyContext, CanManageInspection]

    def get(self, request, po_item_id):
        po_item = get_object_or_404(
            POItemReceipt,
            id=po_item_id,
            po_receipt__vehicle_entry__company=request.company.company
        )
        try:
            inspection = po_item.inspection
            serializer = RawMaterialInspectionSerializer(inspection)
            return Response(serializer.data)
        except RawMaterialInspection.DoesNotExist:
            return Response(
                {"detail": "Inspection not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, po_item_id):
        po_item = get_object_or_404(
            POItemReceipt,
            id=po_item_id,
            po_receipt__vehicle_entry__company=request.company.company
        )

        serializer = RawMaterialInspectionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        material_type_id = data.pop("material_type_id", None)
        material_type = None
        if material_type_id:
            material_type = get_object_or_404(
                MaterialType,
                id=material_type_id,
                company=request.company.company
            )

        inspection, created = RawMaterialInspection.objects.get_or_create(
            po_item_receipt=po_item,
            defaults={
                "report_no": RawMaterialInspection.generate_report_no(),
                "internal_lot_no": RawMaterialInspection.generate_lot_no(),
                "material_type": material_type,
                "created_by": request.user,
                **data
            }
        )

        if not created:
            if inspection.is_locked:
                return Response(
                    {"detail": "Inspection is locked"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            for key, value in data.items():
                setattr(inspection, key, value)
            if material_type:
                inspection.material_type = material_type
            inspection.updated_by = request.user
            inspection.save()

        # Create parameter results if material type has parameters
        if material_type and created:
            for param in material_type.qc_parameters.filter(is_active=True):
                InspectionParameterResult.objects.get_or_create(
                    inspection=inspection,
                    parameter_master=param,
                    defaults={
                        "parameter_name": param.parameter_name,
                        "standard_value": param.standard_value,
                        "created_by": request.user,
                    }
                )

        # Update vehicle entry status
        entry = po_item.po_receipt.vehicle_entry
        if entry.status == GateEntryStatus.ARRIVAL_SLIP_SUBMITTED:
            entry.status = GateEntryStatus.QC_PENDING
            entry.save(update_fields=["status"])

        return Response(
            RawMaterialInspectionSerializer(inspection).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class InspectionParameterResultsAPI(APIView):
    """Update parameter results for an inspection"""
    permission_classes = [IsAuthenticated, HasCompanyContext, CanManageInspection]

    def get(self, request, inspection_id):
        inspection = get_object_or_404(
            RawMaterialInspection,
            id=inspection_id,
            po_item_receipt__po_receipt__vehicle_entry__company=request.company.company
        )
        results = inspection.parameter_results.all()
        serializer = InspectionParameterResultSerializer(results, many=True)
        return Response(serializer.data)

    def post(self, request, inspection_id):
        inspection = get_object_or_404(
            RawMaterialInspection,
            id=inspection_id,
            po_item_receipt__po_receipt__vehicle_entry__company=request.company.company
        )

        if inspection.is_locked:
            return Response(
                {"detail": "Inspection is locked"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ParameterResultBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        results_data = serializer.validated_data.get("results", [])
        updated_results = []

        for result_data in results_data:
            param_id = result_data.pop("parameter_master_id")
            result, _ = InspectionParameterResult.objects.get_or_create(
                inspection=inspection,
                parameter_master_id=param_id,
                defaults={"created_by": request.user}
            )

            for key, value in result_data.items():
                setattr(result, key, value)
            result.updated_by = request.user
            result.save()
            updated_results.append(result)

        return Response(
            InspectionParameterResultSerializer(updated_results, many=True).data,
            status=status.HTTP_200_OK
        )


class InspectionSubmitAPI(APIView):
    """Submit inspection for QA Chemist approval"""
    permission_classes = [IsAuthenticated, HasCompanyContext, CanSubmitInspection]

    def post(self, request, inspection_id):
        inspection = get_object_or_404(
            RawMaterialInspection,
            id=inspection_id,
            po_item_receipt__po_receipt__vehicle_entry__company=request.company.company
        )

        if inspection.is_locked:
            return Response(
                {"detail": "Inspection is locked"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if inspection.workflow_status != InspectionWorkflowStatus.DRAFT:
            return Response(
                {"detail": "Already submitted"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check mandatory parameters
        mandatory_params = inspection.parameter_results.filter(
            parameter_master__is_mandatory=True,
            result_value=""
        )
        if mandatory_params.exists():
            return Response(
                {"detail": "All mandatory parameters must have results"},
                status=status.HTTP_400_BAD_REQUEST
            )

        inspection.submit_for_approval()

        # Update vehicle entry status
        entry = inspection.po_item_receipt.po_receipt.vehicle_entry
        if entry.status == GateEntryStatus.QC_PENDING:
            entry.status = GateEntryStatus.QC_IN_REVIEW
            entry.save(update_fields=["status"])

        return Response(
            RawMaterialInspectionSerializer(inspection).data,
            status=status.HTTP_200_OK
        )


# ==================== Approval APIs ====================

class InspectionApproveChemistAPI(APIView):
    """QA Chemist approval"""
    permission_classes = [IsAuthenticated, HasCompanyContext, CanApproveAsChemist]

    def post(self, request, inspection_id):
        inspection = get_object_or_404(
            RawMaterialInspection,
            id=inspection_id,
            po_item_receipt__po_receipt__vehicle_entry__company=request.company.company
        )

        if inspection.is_locked:
            return Response(
                {"detail": "Inspection is locked"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if inspection.workflow_status != InspectionWorkflowStatus.SUBMITTED:
            return Response(
                {"detail": "Inspection must be submitted first"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        inspection.approve_by_chemist(
            user=request.user,
            remarks=serializer.validated_data.get("remarks", "")
        )

        # Update vehicle entry status
        entry = inspection.po_item_receipt.po_receipt.vehicle_entry
        if entry.status == GateEntryStatus.QC_IN_REVIEW:
            entry.status = GateEntryStatus.QC_AWAITING_QAM
            entry.save(update_fields=["status"])

        return Response(
            RawMaterialInspectionSerializer(inspection).data,
            status=status.HTTP_200_OK
        )


class InspectionApproveQAMAPI(APIView):
    """QA Manager approval"""
    permission_classes = [IsAuthenticated, HasCompanyContext, CanApproveAsQAM]

    def post(self, request, inspection_id):
        inspection = get_object_or_404(
            RawMaterialInspection,
            id=inspection_id,
            po_item_receipt__po_receipt__vehicle_entry__company=request.company.company
        )

        if inspection.is_locked:
            return Response(
                {"detail": "Inspection is locked"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if inspection.workflow_status != InspectionWorkflowStatus.QA_CHEMIST_APPROVED:
            return Response(
                {"detail": "QA Chemist must approve first"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        final_status_str = serializer.validated_data.get("final_status", "ACCEPTED")
        final_status = getattr(InspectionStatus, final_status_str, InspectionStatus.ACCEPTED)

        inspection.approve_by_qam(
            user=request.user,
            remarks=serializer.validated_data.get("remarks", ""),
            final_status=final_status
        )

        # Check if all inspections for this entry are completed
        entry = inspection.po_item_receipt.po_receipt.vehicle_entry
        all_completed = True
        for po_receipt in entry.po_receipts.all():
            for po_item in po_receipt.items.all():
                if hasattr(po_item, "inspection"):
                    if po_item.inspection.workflow_status != InspectionWorkflowStatus.QAM_APPROVED:
                        all_completed = False
                        break
            if not all_completed:
                break

        if all_completed:
            entry.status = GateEntryStatus.QC_COMPLETED
            entry.save(update_fields=["status"])

        return Response(
            RawMaterialInspectionSerializer(inspection).data,
            status=status.HTTP_200_OK
        )


class InspectionRejectAPI(APIView):
    """Reject inspection - sends back to security guard"""
    permission_classes = [IsAuthenticated, HasCompanyContext, CanRejectInspection]

    def post(self, request, inspection_id):
        inspection = get_object_or_404(
            RawMaterialInspection,
            id=inspection_id,
            po_item_receipt__po_receipt__vehicle_entry__company=request.company.company
        )

        if inspection.is_locked:
            return Response(
                {"detail": "Inspection is locked"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        remarks = serializer.validated_data.get("remarks", "")
        inspection.reject(remarks=remarks)

        # Update vehicle entry status and arrival slip
        entry = inspection.po_item_receipt.po_receipt.vehicle_entry
        entry.status = GateEntryStatus.ARRIVAL_SLIP_REJECTED
        entry.save(update_fields=["status"])

        if hasattr(entry, "arrival_slip"):
            entry.arrival_slip.reject_by_qa(remarks=remarks)

        return Response(
            RawMaterialInspectionSerializer(inspection).data,
            status=status.HTTP_200_OK
        )
