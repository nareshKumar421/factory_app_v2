# quality_control/admin.py
"""
Enhanced Quality Control Admin Configuration for Factory Jivo Wellness
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    QCInspection,
    MaterialType,
    QCParameterMaster,
    MaterialArrivalSlip,
    RawMaterialInspection,
    InspectionParameterResult,
)
from .enums import QCStatus, InspectionStatus, InspectionWorkflowStatus


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


# ==================== Material Type Admin ====================

@admin.register(MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "company", "is_active", "created_at")
    list_filter = ("company", "is_active", "created_at")
    search_fields = ("code", "name", "description")
    ordering = ("code",)
    list_per_page = 25

    fieldsets = (
        (None, {
            "fields": ("code", "name", "description", "company"),
        }),
        ("Status", {
            "fields": ("is_active",),
        }),
        ("Audit", {
            "fields": ("created_by", "created_at", "updated_by", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ("created_by", "created_at", "updated_by", "updated_at")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# ==================== QC Parameter Master Admin ====================

class QCParameterMasterInline(admin.TabularInline):
    model = QCParameterMaster
    extra = 1
    fields = (
        "parameter_code", "parameter_name", "standard_value",
        "parameter_type", "min_value", "max_value", "uom",
        "sequence", "is_mandatory", "is_active"
    )


@admin.register(QCParameterMaster)
class QCParameterMasterAdmin(admin.ModelAdmin):
    list_display = (
        "parameter_code", "parameter_name", "material_type",
        "standard_value", "parameter_type", "sequence",
        "is_mandatory", "is_active"
    )
    list_filter = ("material_type", "parameter_type", "is_mandatory", "is_active")
    search_fields = ("parameter_code", "parameter_name", "material_type__name")
    ordering = ("material_type", "sequence")
    list_per_page = 25

    fieldsets = (
        ("Material Type", {
            "fields": ("material_type",),
        }),
        ("Parameter Definition", {
            "fields": ("parameter_code", "parameter_name", "standard_value", "parameter_type"),
        }),
        ("Validation", {
            "fields": ("min_value", "max_value", "uom"),
        }),
        ("Display", {
            "fields": ("sequence", "is_mandatory", "is_active"),
        }),
        ("Audit", {
            "fields": ("created_by", "created_at", "updated_by", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ("created_by", "created_at", "updated_by", "updated_at")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# ==================== Material Arrival Slip Admin ====================

@admin.register(MaterialArrivalSlip)
class MaterialArrivalSlipAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle_entry", "particulars_short", "party_name",
        "arrival_datetime", "status_badge", "is_submitted",
        "submitted_at", "created_at"
    )
    list_filter = ("status", "is_submitted", "weighing_required", "created_at")
    search_fields = (
        "vehicle_entry__entry_no", "particulars", "party_name",
        "commercial_invoice_no", "eway_bill_no", "bilty_no"
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 25

    fieldsets = (
        ("Vehicle Entry", {
            "fields": ("vehicle_entry",),
        }),
        ("Arrival Information", {
            "fields": ("particulars", "arrival_datetime", "weighing_required"),
        }),
        ("Party Information", {
            "fields": ("party_name", "billing_qty", "billing_uom"),
        }),
        ("Transport Details", {
            "fields": ("truck_no_as_per_bill",),
        }),
        ("Document References", {
            "fields": ("commercial_invoice_no", "eway_bill_no", "bilty_no"),
        }),
        ("Certificates", {
            "fields": ("has_certificate_of_analysis", "has_certificate_of_quantity"),
        }),
        ("Status", {
            "fields": ("status", "is_submitted", "submitted_at", "submitted_by", "in_time_to_qa"),
        }),
        ("Remarks", {
            "fields": ("remarks",),
        }),
        ("Audit", {
            "fields": ("created_by", "created_at", "updated_by", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = (
        "status", "is_submitted", "submitted_at", "submitted_by", "in_time_to_qa",
        "created_by", "created_at", "updated_by", "updated_at"
    )

    @admin.display(description="Particulars")
    def particulars_short(self, obj):
        if len(obj.particulars) > 40:
            return obj.particulars[:37] + "..."
        return obj.particulars

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {
            "DRAFT": "#3498db",
            "SUBMITTED": "#27ae60",
            "REJECTED": "#e74c3c",
        }
        color = colors.get(obj.status, "#95a5a6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# ==================== Inspection Parameter Result Inline ====================

class InspectionParameterResultInline(admin.TabularInline):
    model = InspectionParameterResult
    extra = 0
    fields = (
        "parameter_name", "standard_value", "result_value",
        "result_numeric", "is_within_spec", "remarks"
    )
    readonly_fields = ("parameter_name", "standard_value")


# ==================== Raw Material Inspection Admin ====================

@admin.register(RawMaterialInspection)
class RawMaterialInspectionAdmin(admin.ModelAdmin):
    list_display = (
        "report_no", "internal_lot_no", "description_short",
        "supplier_name", "inspection_date", "workflow_status_badge",
        "final_status_badge", "qa_chemist", "qam", "is_locked"
    )
    list_filter = (
        "workflow_status", "final_status", "is_locked",
        "inspection_date", "material_type", "created_at"
    )
    search_fields = (
        "report_no", "internal_lot_no", "description_of_material",
        "supplier_name", "manufacturer_name", "purchase_order_no",
        "invoice_bill_no", "sap_code"
    )
    ordering = ("-created_at",)
    date_hierarchy = "inspection_date"
    list_per_page = 25
    inlines = [InspectionParameterResultInline]

    fieldsets = (
        ("Identifiers", {
            "fields": ("report_no", "internal_lot_no", "po_item_receipt"),
        }),
        ("Inspection Details", {
            "fields": ("inspection_date", "description_of_material", "sap_code", "material_type"),
        }),
        ("Supplier Information", {
            "fields": ("supplier_name", "manufacturer_name", "supplier_batch_lot_no"),
        }),
        ("Order Information", {
            "fields": ("unit_packing", "purchase_order_no", "invoice_bill_no", "vehicle_no"),
        }),
        ("Status", {
            "fields": ("workflow_status", "final_status", "is_locked"),
        }),
        ("QA Chemist Approval", {
            "fields": ("qa_chemist", "qa_chemist_approved_at", "qa_chemist_remarks"),
        }),
        ("QA Manager Approval", {
            "fields": ("qam", "qam_approved_at", "qam_remarks"),
        }),
        ("Remarks", {
            "fields": ("remarks",),
        }),
        ("Audit", {
            "fields": ("created_by", "created_at", "updated_by", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = (
        "report_no", "internal_lot_no", "workflow_status", "is_locked",
        "qa_chemist", "qa_chemist_approved_at", "qam", "qam_approved_at",
        "created_by", "created_at", "updated_by", "updated_at"
    )

    @admin.display(description="Description")
    def description_short(self, obj):
        if len(obj.description_of_material) > 40:
            return obj.description_of_material[:37] + "..."
        return obj.description_of_material

    @admin.display(description="Workflow")
    def workflow_status_badge(self, obj):
        colors = {
            InspectionWorkflowStatus.DRAFT: "#3498db",
            InspectionWorkflowStatus.SUBMITTED: "#f39c12",
            InspectionWorkflowStatus.QA_CHEMIST_APPROVED: "#9b59b6",
            InspectionWorkflowStatus.QAM_APPROVED: "#27ae60",
            InspectionWorkflowStatus.COMPLETED: "#2c3e50",
        }
        color = colors.get(obj.workflow_status, "#95a5a6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_workflow_status_display()
        )

    @admin.display(description="Final Status")
    def final_status_badge(self, obj):
        colors = {
            InspectionStatus.PENDING: "#f39c12",
            InspectionStatus.ACCEPTED: "#27ae60",
            InspectionStatus.REJECTED: "#e74c3c",
            InspectionStatus.HOLD: "#9b59b6",
        }
        color = colors.get(obj.final_status, "#95a5a6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_final_status_display()
        )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
            if not obj.report_no:
                obj.report_no = RawMaterialInspection.generate_report_no()
            if not obj.internal_lot_no:
                obj.internal_lot_no = RawMaterialInspection.generate_lot_no()
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# ==================== Inspection Parameter Result Admin ====================

@admin.register(InspectionParameterResult)
class InspectionParameterResultAdmin(admin.ModelAdmin):
    list_display = (
        "inspection", "parameter_name", "standard_value",
        "result_value", "result_numeric", "is_within_spec"
    )
    list_filter = ("is_within_spec", "parameter_master__material_type")
    search_fields = (
        "inspection__report_no", "parameter_name", "result_value"
    )
    ordering = ("inspection", "parameter_master__sequence")
    list_per_page = 25

    fieldsets = (
        ("Inspection", {
            "fields": ("inspection", "parameter_master"),
        }),
        ("Parameter", {
            "fields": ("parameter_name", "standard_value"),
        }),
        ("Results", {
            "fields": ("result_value", "result_numeric", "is_within_spec"),
        }),
        ("Remarks", {
            "fields": ("remarks",),
        }),
        ("Audit", {
            "fields": ("created_by", "created_at", "updated_by", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ("parameter_name", "standard_value", "created_by", "created_at", "updated_by", "updated_at")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
