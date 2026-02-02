# quality_control/admin.py
"""
Enhanced Quality Control Admin Configuration for Factory Jivo Wellness
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import QCInspection
from .enums import QCStatus


@admin.register(QCInspection)
class QCInspectionAdmin(admin.ModelAdmin):
    """
    Comprehensive QC Inspection Admin with all features
    """
    list_display = (
        "po_item_receipt_link",
        "item_name_display",
        "qc_status_badge",
        "sample_collected_display",
        "batch_no",
        "expiry_date",
        "inspected_by_link",
        "inspection_time",
        "is_locked_display",
        "is_active_display",
    )
    list_display_links = ("po_item_receipt_link",)
    list_filter = (
        "qc_status",
        "sample_collected",
        "is_locked",
        "is_active",
        "expiry_date",
        "inspection_time",
        "created_at",
    )
    search_fields = (
        "po_item_receipt__po_item_code",
        "po_item_receipt__item_name",
        "po_item_receipt__po_receipt__po_number",
        "po_item_receipt__po_receipt__supplier_name",
        "batch_no",
        "inspected_by__email",
        "inspected_by__full_name",
        "remarks",
    )
    ordering = ("-inspection_time",)
    date_hierarchy = "inspection_time"
    list_per_page = 25

    autocomplete_fields = ["po_item_receipt", "inspected_by"]

    fieldsets = (
        ("Item Information", {
            "fields": ("po_item_receipt",),
            "description": "PO item being inspected"
        }),
        ("QC Status", {
            "fields": ("qc_status", "sample_collected"),
            "classes": ("wide",),
        }),
        ("Batch Information", {
            "fields": ("batch_no", "expiry_date"),
            "classes": ("wide",),
        }),
        ("Inspector Information", {
            "fields": ("inspected_by", "inspection_time"),
        }),
        ("Additional Information", {
            "fields": ("remarks",),
        }),
        ("Lock Status", {
            "fields": ("is_locked", "is_active"),
        }),
        ("Audit Information", {
            "fields": ("created_by", "created_at", "updated_by", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    readonly_fields = (
        "inspection_time", "is_locked",
        "created_by", "created_at", "updated_by", "updated_at"
    )

    @admin.display(description="PO Item", ordering="po_item_receipt__po_item_code")
    def po_item_receipt_link(self, obj):
        url = reverse('admin:raw_material_gatein_poitemreceipt_change', args=[obj.po_item_receipt.id])
        return format_html(
            '<a href="{}" style="font-weight: bold;">{}</a>',
            url, obj.po_item_receipt.po_item_code
        )

    @admin.display(description="Item Name", ordering="po_item_receipt__item_name")
    def item_name_display(self, obj):
        name = obj.po_item_receipt.item_name
        if len(name) > 30:
            return format_html(
                '<span title="{}">{}</span>',
                name, name[:27] + "..."
            )
        return name

    @admin.display(description="QC Status", ordering="qc_status")
    def qc_status_badge(self, obj):
        colors = {
            QCStatus.PENDING: "#f39c12",
            QCStatus.PASSED: "#27ae60",
            QCStatus.FAILED: "#e74c3c",
        }
        color = colors.get(obj.qc_status, "#95a5a6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_qc_status_display()
        )

    @admin.display(description="Sample", boolean=True, ordering="sample_collected")
    def sample_collected_display(self, obj):
        return obj.sample_collected

    @admin.display(description="Inspector", ordering="inspected_by__full_name")
    def inspected_by_link(self, obj):
        if obj.inspected_by:
            url = reverse('admin:accounts_user_change', args=[obj.inspected_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.inspected_by.full_name)
        return format_html('<span style="color: #999;">{}</span>', "Not Assigned")

    @admin.display(description="Locked", boolean=True, ordering="is_locked")
    def is_locked_display(self, obj):
        return obj.is_locked

    @admin.display(description="Active", boolean=True, ordering="is_active")
    def is_active_display(self, obj):
        return obj.is_active

    # Admin actions
    @admin.action(description="Mark as QC Passed")
    def mark_passed(self, request, queryset):
        for qc in queryset.filter(is_locked=False):
            qc.qc_status = QCStatus.PASSED
            qc.inspected_by = request.user
            qc.save()
        self.message_user(request, f"QC inspection(s) marked as PASSED (unlocked items only).")

    @admin.action(description="Mark as QC Failed")
    def mark_failed(self, request, queryset):
        for qc in queryset.filter(is_locked=False):
            qc.qc_status = QCStatus.FAILED
            qc.inspected_by = request.user
            qc.save()
        self.message_user(request, f"QC inspection(s) marked as FAILED (unlocked items only).")

    @admin.action(description="Reset to Pending (Admin Only)")
    def reset_to_pending(self, request, queryset):
        # This is an admin override action
        updated = queryset.update(qc_status=QCStatus.PENDING, is_locked=False)
        self.message_user(request, f"{updated} QC inspection(s) reset to PENDING.")

    @admin.action(description="Mark sample collected")
    def mark_sample_collected(self, request, queryset):
        updated = queryset.update(sample_collected=True)
        self.message_user(request, f"{updated} inspection(s) marked as sample collected.")

    @admin.action(description="Unlock selected inspections (Admin)")
    def unlock_inspections(self, request, queryset):
        updated = queryset.update(is_locked=False)
        self.message_user(request, f"{updated} inspection(s) unlocked.")

    @admin.action(description="Assign me as inspector")
    def assign_me(self, request, queryset):
        updated = queryset.filter(is_locked=False).update(inspected_by=request.user)
        self.message_user(request, f"{updated} inspection(s) assigned to you.")

    @admin.action(description="Activate selected")
    def activate_inspections(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} inspection(s) activated.")

    @admin.action(description="Deactivate selected")
    def deactivate_inspections(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} inspection(s) deactivated.")

    actions = [
        "mark_passed", "mark_failed", "reset_to_pending",
        "mark_sample_collected", "unlock_inspections",
        "assign_me", "activate_inspections", "deactivate_inspections"
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'po_item_receipt', 'po_item_receipt__po_receipt',
            'inspected_by', 'created_by', 'updated_by'
        )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        # Set inspector if not set
        if not obj.inspected_by:
            obj.inspected_by = request.user
        super().save_model(request, obj, form, change)
