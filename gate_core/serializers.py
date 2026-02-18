from .models import UnitChoice
from rest_framework import serializers
from .models import GateAttachment

class UnitChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitChoice
        fields = ['id', 'name']


class GateAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GateAttachment
        fields = ['id', 'file', 'uploaded_at']