from rest_framework import serializers


class POItemSerializer(serializers.Serializer):
    po_item_code = serializers.CharField()
    item_name = serializers.CharField()
    ordered_qty = serializers.DecimalField(max_digits=12, decimal_places=3)
    received_qty = serializers.DecimalField(max_digits=12, decimal_places=3)
    remaining_qty = serializers.DecimalField(max_digits=12, decimal_places=3)
    uom = serializers.CharField()


class POSerializer(serializers.Serializer):
    po_number = serializers.CharField()
    supplier_code = serializers.CharField()
    supplier_name = serializers.CharField()
    items = POItemSerializer(many=True)
