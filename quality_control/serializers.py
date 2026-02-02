from rest_framework import serializers
from quality_control.models.qc_inspection import QCInspection


class QCInspectionSerializer(serializers.ModelSerializer):
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
