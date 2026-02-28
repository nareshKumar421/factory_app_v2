from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()


# -------------------------
# Masters
# -------------------------
class PersonTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonType
        fields = "__all__"


class GateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gate
        fields = "__all__"


class ContractorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contractor
        fields = "__all__"


class VisitorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Visitor
        fields = "__all__"


class LabourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labour
        fields = "__all__"


# -------------------------
# Entry Log
# -------------------------
class EntryLogSerializer(serializers.ModelSerializer):
    person_type = PersonTypeSerializer(read_only=True)
    gate_in = GateSerializer(read_only=True)
    gate_out = GateSerializer(read_only=True)
    class Meta:
        model = EntryLog
        fields = "__all__"
        read_only_fields = ["entry_time", "created_at", "updated_at"]


# -------------------------
# Bulk Entry / Exit
# -------------------------
class BulkLabourEntryItemSerializer(serializers.Serializer):
    labour_id = serializers.IntegerField()
    purpose = serializers.CharField(max_length=255, required=False, allow_blank=True)
    remarks = serializers.CharField(required=False, allow_blank=True)
    vehicle_no = serializers.CharField(max_length=50, required=False, allow_blank=True)


class BulkLabourEntryRequestSerializer(serializers.Serializer):
    contractor_id = serializers.IntegerField()
    gate_in = serializers.IntegerField()
    person_type = serializers.IntegerField()
    approved_by = serializers.IntegerField(required=False)
    actual_entry_time = serializers.DateTimeField(required=False)
    labours = BulkLabourEntryItemSerializer(many=True)

    def validate_labours(self, value):
        if not value:
            raise serializers.ValidationError("At least one labour is required.")
        labour_ids = [item["labour_id"] for item in value]
        if len(labour_ids) != len(set(labour_ids)):
            raise serializers.ValidationError("Duplicate labour IDs in request.")
        return value

    def validate(self, data):
        # Contractor
        try:
            contractor = Contractor.objects.get(id=data["contractor_id"], is_active=True)
        except Contractor.DoesNotExist:
            raise serializers.ValidationError({"contractor_id": "Contractor not found or inactive."})

        # Gate
        try:
            Gate.objects.get(id=data["gate_in"], is_active=True)
        except Gate.DoesNotExist:
            raise serializers.ValidationError({"gate_in": "Gate not found or inactive."})

        # PersonType
        try:
            PersonType.objects.get(id=data["person_type"])
        except PersonType.DoesNotExist:
            raise serializers.ValidationError({"person_type": "Person type not found."})

        # approved_by
        if data.get("approved_by"):
            try:
                User.objects.get(id=data["approved_by"])
            except User.DoesNotExist:
                raise serializers.ValidationError({"approved_by": "User not found."})

        # All labour_ids must belong to the contractor and be active
        labour_ids = [item["labour_id"] for item in data["labours"]]
        valid_labours = Labour.objects.filter(
            id__in=labour_ids, contractor=contractor, is_active=True
        ).values_list("id", flat=True)
        invalid_ids = set(labour_ids) - set(valid_labours)
        if invalid_ids:
            raise serializers.ValidationError({
                "labours": f"Labour IDs {list(invalid_ids)} do not belong to this contractor or are inactive."
            })

        return data


class BulkLabourExitItemSerializer(serializers.Serializer):
    labour_id = serializers.IntegerField()


class BulkLabourExitRequestSerializer(serializers.Serializer):
    contractor_id = serializers.IntegerField()
    gate_out = serializers.IntegerField()
    labours = BulkLabourExitItemSerializer(many=True)

    def validate_labours(self, value):
        if not value:
            raise serializers.ValidationError("At least one labour is required.")
        labour_ids = [item["labour_id"] for item in value]
        if len(labour_ids) != len(set(labour_ids)):
            raise serializers.ValidationError("Duplicate labour IDs in request.")
        return value

    def validate(self, data):
        # Contractor
        try:
            Contractor.objects.get(id=data["contractor_id"], is_active=True)
        except Contractor.DoesNotExist:
            raise serializers.ValidationError({"contractor_id": "Contractor not found or inactive."})

        # Gate
        try:
            Gate.objects.get(id=data["gate_out"], is_active=True)
        except Gate.DoesNotExist:
            raise serializers.ValidationError({"gate_out": "Gate not found or inactive."})

        return data
