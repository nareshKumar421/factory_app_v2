from rest_framework import serializers
from .models import *


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
