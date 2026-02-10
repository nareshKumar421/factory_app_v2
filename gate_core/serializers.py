from .models import UnitChoice
from rest_framework import serializers

class UnitChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitChoice
        fields = ['id', 'name']