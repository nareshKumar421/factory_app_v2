from rest_framework import serializers
from .models import Driver


class DriverSerializer(serializers.ModelSerializer):


    class Meta:
        model = Driver
        fields = [
            "id",
            "name",
            "mobile_no",
            "license_no",
            "id_proof_type",
            "id_proof_number",
            "photo",
            "created_at",
        ]
        read_only_fields = ("id", "created_at")


class DriverNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ["id", "name"]