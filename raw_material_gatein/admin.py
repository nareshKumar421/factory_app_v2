# raw_material_gatein/admin.py
"""
Enhanced Raw Material Gate-In Admin Configuration for Factory Jivo Wellness
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Count
from .models import POReceipt, POItemReceipt


class POItemInline(admin.TabularInline):
    """Inline for PO Items within PO Receipt"""
    model = POItemReceipt
    extra = 0
    fields = (
        "po_item_code", "item_name", "uom",
        "ordered_qty", "received_qty", "short_qty",
        "accepted_qty", "rejected_qty", "is_active"
    )
    readonly_fields = ("short_qty",)
    show_change_link = True
    classes = ("collapse",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('po_receipt')


@admin.register(POReceipt)
class POReceiptAdmin(admin.ModelAdmin):
    """
    Comprehensive PO Receipt Admin with all features
    """
    list_display = (
        "po_number",
        "vehicle_entry_link",
        "supplier_code",
        "supplier_name",
        "invoice_no",
        "invoice_date",
        "challan_no",
        "item_count",
        "total_received_qty",
        "is_active_display",
        "created_at",
    )
    list_display_links = ("po_number",)
    list_filter = (
        "is_active",
        "invoice_date",
        "created_at",
    )
    search_fields = (
        "po_number",
        "supplier_code",
        "supplier_name",
        "invoice_no",
        "challan_no",
        "vehicle_entry__entry_no",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 25

    autocomplete_fields = ["vehicle_entry"]
    inlines = [POItemInline]

    fieldsets = (
        ("PO Information", {
            "fields": ("po_number", "vehicle_entry"),
            "description": "Purchase order details"
        }),
        ("Supplier Details", {
            "fields": ("supplier_code", "supplier_name"),
            "classes": ("wide",),
        }),
        ("Invoice & Challan", {
            "fields": ("invoice_no", "invoice_date", "challan_no"),
            "classes": ("wide",),
        }),
        ("Status", {
            "fields": ("is_active",),
        }),
        ("Audit Information", {
            "fields": ("created_by", "created_at", "updated_by", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    readonly_fields = ("created_by", "created_at", "updated_by", "updated_at")

    @admin.display(description="Gate Entry", ordering="vehicle_entry__entry_no")
    def vehicle_entry_link(self, obj):
        url = reverse('admin:driver_management_vehicleentry_change', args=[obj.vehicle_entry.id])
        return format_html(
            '<a href="{}" style="font-weight: bold;">{}</a>',
            url, obj.vehicle_entry.entry_no
        )

    @admin.display(description="Items")
    def item_count(self, obj):
        count = obj.items.count()
        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>',
                count
            )
        return format_html('<span style="color: #999;">{}</span>', "0")

    @admin.display(description="Total Received")
    def total_received_qty(self, obj):
        total = obj.items.aggregate(total=Sum('received_qty'))['total']
        if total:
            return format_html(
                '<span style="font-weight: bold;">{}</span>',
                f"{total:.2f}"
            )
        return format_html('<span style="color: #999;">{}</span>', "0.00")

    @admin.display(description="Active", boolean=True, ordering="is_active")
    def is_active_display(self, obj):
        return obj.is_active

    # Admin actions
    @admin.action(description="Activate selected PO receipts")
    def activate_receipts(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} PO receipt(s) activated.")

    @admin.action(description="Deactivate selected PO receipts")
    def deactivate_receipts(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} PO receipt(s) deactivated.")

    actions = ["activate_receipts", "deactivate_receipts"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'vehicle_entry', 'created_by', 'updated_by'
        ).prefetch_related('items')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(POItemReceipt)
class POItemReceiptAdmin(admin.ModelAdmin):
    """
    Comprehensive PO Item Receipt Admin with all features
    """
    list_display = (
        "po_item_code",
        "item_name",
        "po_receipt_link",
        "uom",
        "ordered_qty",
        "received_qty",
        "short_qty_display",
        "accepted_qty",
        "rejected_qty",
        "qc_status_badge",
        "is_active_display",
    )
    list_display_links = ("po_item_code", "item_name")
    list_filter = (
        "is_active",
        "uom",
        "created_at",
    )
    search_fields = (
        "po_item_code",
        "item_name",
        "po_receipt__po_number",
        "po_receipt__supplier_name",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 25

    autocomplete_fields = ["po_receipt"]

    fieldsets = (
        ("Item Information", {
            "fields": ("po_receipt", "po_item_code", "item_name", "uom"),
            "description": "PO line item details"
        }),
        ("Quantities", {
            "fields": (
                ("ordered_qty", "received_qty"),
                ("accepted_qty", "rejected_qty"),
                "short_qty",
            ),
            "classes": ("wide",),
        }),
        ("Status", {
            "fields": ("is_active",),
        }),
        ("Audit Information", {
            "fields": ("created_by", "created_at", "updated_by", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    readonly_fields = ("short_qty", "created_by", "created_at", "updated_by", "updated_at")

    @admin.display(description="PO Receipt", ordering="po_receipt__po_number")
    def po_receipt_link(self, obj):
        url = reverse('admin:raw_material_gatein_poreceipt_change', args=[obj.po_receipt.id])
        return format_html(
            '<a href="{}">{}</a>',
            url, obj.po_receipt.po_number
        )

    @admin.display(description="Short Qty", ordering="short_qty")
    def short_qty_display(self, obj):
        if obj.short_qty > 0:
            return format_html(
                '<span style="color: #e74c3c; font-weight: bold;">{}</span>',
                f"{obj.short_qty:.2f}"
            )
        elif obj.short_qty < 0:
            return format_html(
                '<span style="color: #27ae60; font-weight: bold;">{}</span>',
                f"{obj.short_qty:.2f}"
            )
        return format_html('<span style="color: #999;">{}</span>', "0.00")

    @admin.display(description="QC Status")
    def qc_status_badge(self, obj):
        # Check new flow: POItemReceipt → arrival_slip → inspection
        arrival_slip = getattr(obj, 'arrival_slip', None)
        if not arrival_slip:
            return format_html(
                '<span style="color: #999; font-size: 11px;">{}</span>',
                "No Slip"
            )

        inspection = getattr(arrival_slip, 'inspection', None)
        if not inspection:
            return format_html(
                '<span style="background-color: #3498db; color: white; padding: 2px 6px; '
                'border-radius: 4px; font-size: 11px;">{}</span>',
                "Slip Only"
            )

        status = inspection.final_status
        colors = {
            "PENDING": "#f39c12",
            "ACCEPTED": "#27ae60",
            "REJECTED": "#e74c3c",
            "HOLD": "#9b59b6",
        }
        color = colors.get(status, "#95a5a6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, status
        )

    @admin.display(description="Active", boolean=True, ordering="is_active")
    def is_active_display(self, obj):
        return obj.is_active

    # Admin actions
    @admin.action(description="Activate selected items")
    def activate_items(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} item(s) activated.")

    @admin.action(description="Deactivate selected items")
    def deactivate_items(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} item(s) deactivated.")

    @admin.action(description="Accept all received quantity")
    def accept_all_received(self, request, queryset):
        for item in queryset:
            item.accepted_qty = item.received_qty
            item.rejected_qty = 0
            item.save()
        self.message_user(request, f"{queryset.count()} item(s) accepted in full.")

    actions = ["activate_items", "deactivate_items", "accept_all_received"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'po_receipt', 'created_by', 'updated_by',
            'arrival_slip', 'arrival_slip__inspection'
        )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
