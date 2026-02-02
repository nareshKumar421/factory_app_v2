# security_checks/admin.py
"""
Enhanced Security Checks Admin Configuration for Factory Jivo Wellness
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import SecurityCheck


@admin.register(SecurityCheck)
class SecurityCheckAdmin(admin.ModelAdmin):
    """
    Comprehensive Security Check Admin with all features
    """
    list_display = (
        "vehicle_entry_link",
        "inspected_by_name",
        "inspection_time",
        "vehicle_condition_badge",
        "tyre_condition_badge",
        "fire_extinguisher_badge",
        "alcohol_test_badge",
        "is_submitted_display",
        "is_active_display",
    )
    list_display_links = ("vehicle_entry_link",)
    list_filter = (
        "is_submitted",
        "is_active",
        "vehicle_condition_ok",
        "tyre_condition_ok",
        "fire_extinguisher_available",
        "alcohol_test_done",
        "alcohol_test_passed",
        "inspection_time",
        "created_at",
    )
    search_fields = (
        "vehicle_entry__entry_no",
        "vehicle_entry__vehicle__vehicle_number",
        "vehicle_entry__driver__name",
        "inspected_by_name",
        "seal_no_before",
        "seal_no_after",
        "remarks",
    )
    ordering = ("-inspection_time",)
    date_hierarchy = "inspection_time"
    list_per_page = 25

    autocomplete_fields = ["vehicle_entry"]

    fieldsets = (
        ("Entry Information", {
            "fields": ("vehicle_entry",),
            "description": "Associated gate entry"
        }),
        ("Vehicle Condition Checks", {
            "fields": (
                "vehicle_condition_ok",
                "tyre_condition_ok",
                "fire_extinguisher_available",
            ),
            "classes": ("wide",),
            "description": "Verify vehicle safety conditions"
        }),
        ("Seal Information", {
            "fields": ("seal_no_before", "seal_no_after"),
            "classes": ("wide",),
        }),
        ("Safety & Compliance", {
            "fields": ("alcohol_test_done", "alcohol_test_passed"),
            "classes": ("wide",),
        }),
        ("Inspector Information", {
            "fields": ("inspected_by_name", "inspection_time"),
        }),
        ("Additional Information", {
            "fields": ("remarks",),
        }),
        ("Status", {
            "fields": ("is_submitted", "is_active"),
        }),
        ("Audit Information", {
            "fields": ("created_by", "created_at", "updated_by", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    readonly_fields = (
        "inspection_time", "created_by", "created_at",
        "updated_by", "updated_at"
    )

    @admin.display(description="Vehicle Entry", ordering="vehicle_entry__entry_no")
    def vehicle_entry_link(self, obj):
        url = reverse('admin:driver_management_vehicleentry_change', args=[obj.vehicle_entry.id])
        return format_html(
            '<a href="{}" style="font-weight: bold;">{}</a>',
            url, obj.vehicle_entry.entry_no
        )

    @admin.display(description="Vehicle OK", boolean=True, ordering="vehicle_condition_ok")
    def vehicle_condition_badge(self, obj):
        return obj.vehicle_condition_ok

    @admin.display(description="Tyre OK", boolean=True, ordering="tyre_condition_ok")
    def tyre_condition_badge(self, obj):
        return obj.tyre_condition_ok

    @admin.display(description="Fire Ext.", boolean=True, ordering="fire_extinguisher_available")
    def fire_extinguisher_badge(self, obj):
        return obj.fire_extinguisher_available

    @admin.display(description="Alcohol Test")
    def alcohol_test_badge(self, obj):
        if not obj.alcohol_test_done:
            return format_html(
                '<span style="color: #999; font-size: 11px;">{}</span>',
                "Not Done"
            )
        if obj.alcohol_test_passed:
            return format_html(
                '<span style="background-color: #27ae60; color: white; padding: 2px 6px; '
                'border-radius: 4px; font-size: 11px;">{}</span>',
                "PASSED"
            )
        return format_html(
            '<span style="background-color: #e74c3c; color: white; padding: 2px 6px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            "FAILED"
        )

    @admin.display(description="Submitted", boolean=True, ordering="is_submitted")
    def is_submitted_display(self, obj):
        return obj.is_submitted

    @admin.display(description="Active", boolean=True, ordering="is_active")
    def is_active_display(self, obj):
        return obj.is_active

    # Admin actions
    @admin.action(description="Mark as Submitted")
    def mark_submitted(self, request, queryset):
        updated = queryset.filter(is_submitted=False).update(is_submitted=True)
        self.message_user(request, f"{updated} security check(s) marked as submitted.")

    @admin.action(description="Unsubmit selected (Reopen)")
    def unsubmit_checks(self, request, queryset):
        updated = queryset.filter(is_submitted=True).update(is_submitted=False)
        self.message_user(request, f"{updated} security check(s) reopened.")

    @admin.action(description="Mark all conditions as OK")
    def mark_all_ok(self, request, queryset):
        updated = queryset.update(
            vehicle_condition_ok=True,
            tyre_condition_ok=True,
            fire_extinguisher_available=True
        )
        self.message_user(request, f"{updated} check(s) marked with all conditions OK.")

    @admin.action(description="Mark alcohol test as passed")
    def mark_alcohol_passed(self, request, queryset):
        updated = queryset.update(alcohol_test_done=True, alcohol_test_passed=True)
        self.message_user(request, f"{updated} check(s) marked with alcohol test passed.")

    @admin.action(description="Activate selected")
    def activate_checks(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} check(s) activated.")

    @admin.action(description="Deactivate selected")
    def deactivate_checks(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} check(s) deactivated.")

    actions = [
        "mark_submitted", "unsubmit_checks", "mark_all_ok",
        "mark_alcohol_passed", "activate_checks", "deactivate_checks"
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'vehicle_entry', 'vehicle_entry__vehicle', 'vehicle_entry__driver',
            'created_by', 'updated_by'
        )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
