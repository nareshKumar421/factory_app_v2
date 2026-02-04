from rest_framework import serializers
from quality_control.models.qc_inspection import QCInspection
from quality_control.models.material_type import MaterialType
from quality_control.models.qc_parameter_master import QCParameterMaster
from quality_control.models.material_arrival_slip import MaterialArrivalSlip
from quality_control.models.raw_material_inspection import RawMaterialInspection
from quality_control.models.inspection_parameter_result import InspectionParameterResult


class QCInspectionSerializer(serializers.ModelSerializer):
    """Legacy serializer for backward compatibility"""
    class Meta:
        model = QCInspection
        fields = [
            "id",
            "qc_status",
            "sample_collected",
            "batch_no",
            "expiry_date",
            "inspected_by",
            "inspection_time",
            "remarks",
            "is_locked",
        ]
        read_only_fields = (
            "id",
            "inspection_time",
            "is_locked",
        )


# ==================== Material Type Serializers ====================

class MaterialTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialType
        fields = [
            "id", "code", "name", "description",
            "company", "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MaterialTypeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialType
        fields = ["code", "name", "description"]


# ==================== QC Parameter Master Serializers ====================

class QCParameterMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = QCParameterMaster
        fields = [
            "id", "material_type", "parameter_name", "parameter_code",
            "standard_value", "parameter_type", "min_value", "max_value",
            "uom", "sequence", "is_mandatory", "is_active",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class QCParameterMasterCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QCParameterMaster
        fields = [
            "parameter_name", "parameter_code", "standard_value",
            "parameter_type", "min_value", "max_value", "uom",
            "sequence", "is_mandatory"
        ]


# ==================== Material Arrival Slip Serializers ====================

class MaterialArrivalSlipSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(
        source="submitted_by.full_name", read_only=True
    )

    class Meta:
        model = MaterialArrivalSlip
        fields = [
            "id", "vehicle_entry", "particulars", "arrival_datetime",
            "weighing_required", "party_name", "billing_qty", "billing_uom",
            "in_time_to_qa", "truck_no_as_per_bill", "commercial_invoice_no",
            "eway_bill_no", "bilty_no", "has_certificate_of_analysis",
            "has_certificate_of_quantity", "status", "is_submitted",
            "submitted_at", "submitted_by", "submitted_by_name", "remarks",
            "created_at", "updated_at"
        ]
        read_only_fields = [
            "id", "status", "is_submitted", "submitted_at",
            "submitted_by", "submitted_by_name", "in_time_to_qa",
            "created_at", "updated_at"
        ]


class MaterialArrivalSlipCreateSerializer(serializers.Serializer):
    """For creation/update by security guard"""
    particulars = serializers.CharField()
    arrival_datetime = serializers.DateTimeField()
    weighing_required = serializers.BooleanField(default=False)
    party_name = serializers.CharField(max_length=200)
    billing_qty = serializers.DecimalField(max_digits=12, decimal_places=3)
    billing_uom = serializers.CharField(max_length=20, required=False, allow_blank=True)
    truck_no_as_per_bill = serializers.CharField(max_length=50)
    commercial_invoice_no = serializers.CharField(max_length=100, required=False, allow_blank=True)
    eway_bill_no = serializers.CharField(max_length=100, required=False, allow_blank=True)
    bilty_no = serializers.CharField(max_length=100, required=False, allow_blank=True)
    has_certificate_of_analysis = serializers.BooleanField(default=False)
    has_certificate_of_quantity = serializers.BooleanField(default=False)
    remarks = serializers.CharField(required=False, allow_blank=True)


# ==================== Inspection Parameter Result Serializers ====================

class InspectionParameterResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionParameterResult
        fields = [
            "id", "parameter_master", "parameter_name", "standard_value",
            "result_value", "result_numeric", "is_within_spec", "remarks"
        ]
        read_only_fields = ["id", "parameter_name", "standard_value"]


class InspectionParameterResultCreateSerializer(serializers.Serializer):
    """For bulk creating/updating parameter results"""
    parameter_master_id = serializers.IntegerField()
    result_value = serializers.CharField(max_length=200, required=False, allow_blank=True)
    result_numeric = serializers.DecimalField(
        max_digits=12, decimal_places=4, required=False, allow_null=True
    )
    is_within_spec = serializers.BooleanField(required=False, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True)


# ==================== Raw Material Inspection Serializers ====================

class RawMaterialInspectionSerializer(serializers.ModelSerializer):
    parameter_results = InspectionParameterResultSerializer(many=True, read_only=True)
    qa_chemist_name = serializers.CharField(source="qa_chemist.full_name", read_only=True)
    qam_name = serializers.CharField(source="qam.full_name", read_only=True)
    material_type_name = serializers.CharField(source="material_type.name", read_only=True)

    class Meta:
        model = RawMaterialInspection
        fields = [
            "id", "po_item_receipt", "report_no", "internal_lot_no",
            "inspection_date", "description_of_material", "sap_code",
            "supplier_name", "manufacturer_name", "supplier_batch_lot_no",
            "unit_packing", "purchase_order_no", "invoice_bill_no",
            "vehicle_no", "material_type", "material_type_name",
            "final_status", "qa_chemist", "qa_chemist_name",
            "qa_chemist_approved_at", "qa_chemist_remarks",
            "qam", "qam_name", "qam_approved_at", "qam_remarks",
            "workflow_status", "is_locked", "remarks",
            "parameter_results", "created_at", "updated_at"
        ]
        read_only_fields = [
            "id", "report_no", "internal_lot_no",
            "qa_chemist", "qa_chemist_name", "qa_chemist_approved_at",
            "qam", "qam_name", "qam_approved_at",
            "workflow_status", "is_locked", "created_at", "updated_at"
        ]


class RawMaterialInspectionCreateSerializer(serializers.Serializer):
    """For creating inspection by QA"""
    inspection_date = serializers.DateField()
    description_of_material = serializers.CharField()
    sap_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    supplier_name = serializers.CharField(max_length=200)
    manufacturer_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    supplier_batch_lot_no = serializers.CharField(max_length=100)
    unit_packing = serializers.CharField(max_length=100, required=False, allow_blank=True)
    purchase_order_no = serializers.CharField(max_length=50)
    invoice_bill_no = serializers.CharField(max_length=100, required=False, allow_blank=True)
    vehicle_no = serializers.CharField(max_length=50, required=False, allow_blank=True)
    material_type_id = serializers.IntegerField(required=False, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True)


class ApprovalSerializer(serializers.Serializer):
    """For approval actions"""
    remarks = serializers.CharField(required=False, allow_blank=True)
    final_status = serializers.ChoiceField(
        choices=["ACCEPTED", "REJECTED", "HOLD"],
        required=False
    )


class ParameterResultBulkUpdateSerializer(serializers.Serializer):
    """For bulk updating parameter results"""
    results = InspectionParameterResultCreateSerializer(many=True)
