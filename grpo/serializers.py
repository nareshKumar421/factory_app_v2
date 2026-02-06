from rest_framework import serializers
from .models import GRPOPosting, GRPOLinePosting


class GRPOLineDetailSerializer(serializers.Serializer):
    """Serializer for GRPO line item details (for preview/preparation)"""
    po_item_receipt_id = serializers.IntegerField()
    item_code = serializers.CharField()
    item_name = serializers.CharField()
    ordered_qty = serializers.DecimalField(max_digits=12, decimal_places=3)
    received_qty = serializers.DecimalField(max_digits=12, decimal_places=3)
    accepted_qty = serializers.DecimalField(max_digits=12, decimal_places=3)
    rejected_qty = serializers.DecimalField(max_digits=12, decimal_places=3)
    uom = serializers.CharField()
    qc_status = serializers.CharField()


class GRPOPreviewSerializer(serializers.Serializer):
    """
    Serializer for GRPO preview data.
    Returns all data needed to post GRPO after gate entry completion.
    """
    vehicle_entry_id = serializers.IntegerField()
    entry_no = serializers.CharField()
    entry_status = serializers.CharField()
    is_ready_for_grpo = serializers.BooleanField()

    po_receipt_id = serializers.IntegerField()
    po_number = serializers.CharField()
    supplier_code = serializers.CharField()
    supplier_name = serializers.CharField()

    invoice_no = serializers.CharField(allow_blank=True)
    invoice_date = serializers.DateField(allow_null=True)
    challan_no = serializers.CharField(allow_blank=True)

    items = GRPOLineDetailSerializer(many=True)

    # GRPO posting status if already attempted
    grpo_status = serializers.CharField(allow_null=True)
    sap_doc_num = serializers.IntegerField(allow_null=True)


class GRPOItemInputSerializer(serializers.Serializer):
    """Serializer for individual item accepted quantity input"""
    po_item_receipt_id = serializers.IntegerField(required=True)
    accepted_qty = serializers.DecimalField(
        max_digits=12, decimal_places=3, required=True, min_value=0
    )


class GRPOPostRequestSerializer(serializers.Serializer):
    """Serializer for GRPO posting request"""
    vehicle_entry_id = serializers.IntegerField(required=True)
    po_receipt_id = serializers.IntegerField(required=True)
    items = GRPOItemInputSerializer(many=True, required=True)
    branch_id = serializers.IntegerField(
        required=True,
        help_text="SAP Branch/Business Place ID (BPLId)"
    )
    warehouse_code = serializers.CharField(required=False, allow_blank=True)
    comments = serializers.CharField(required=False, allow_blank=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item with accepted quantity is required")
        return value


class GRPOLinePostingSerializer(serializers.ModelSerializer):
    item_code = serializers.CharField(source='po_item_receipt.po_item_code', read_only=True)
    item_name = serializers.CharField(source='po_item_receipt.item_name', read_only=True)

    class Meta:
        model = GRPOLinePosting
        fields = [
            'id',
            'item_code',
            'item_name',
            'quantity_posted',
            'base_entry',
            'base_line'
        ]


class GRPOPostingSerializer(serializers.ModelSerializer):
    lines = GRPOLinePostingSerializer(many=True, read_only=True)
    po_number = serializers.CharField(source='po_receipt.po_number', read_only=True)
    entry_no = serializers.CharField(source='vehicle_entry.entry_no', read_only=True)

    class Meta:
        model = GRPOPosting
        fields = [
            'id',
            'vehicle_entry',
            'entry_no',
            'po_receipt',
            'po_number',
            'sap_doc_entry',
            'sap_doc_num',
            'sap_doc_total',
            'status',
            'error_message',
            'posted_at',
            'posted_by',
            'created_at',
            'lines'
        ]


class GRPOPostResponseSerializer(serializers.Serializer):
    """Serializer for GRPO post response"""
    success = serializers.BooleanField()
    grpo_posting_id = serializers.IntegerField()
    sap_doc_entry = serializers.IntegerField(allow_null=True)
    sap_doc_num = serializers.IntegerField(allow_null=True)
    sap_doc_total = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    message = serializers.CharField()
