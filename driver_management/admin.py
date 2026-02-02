# driver_management/admin.py
"""
Enhanced Driver Management Admin Configuration for Factory Jivo Wellness
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Driver, VehicleEntry


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    """
    Comprehensive Driver Admin with all features
    """
    list_display = (
        "name",
        "mobile_no",
        "license_no",
        "id_proof_type",
        "id_proof_number",
        "photo_preview",
        "is_active_display",
        "gate_entry_count",
        "created_at",
    )
    list_display_links = ("name", "license_no")
    list_filter = (
        "is_active",
        "id_proof_type",
        "created_at",
    )
    search_fields = (
        "name",
        "mobile_no",
        "license_no",
        "id_proof_number",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 25

    fieldsets = (
        ("Driver Information", {
            "fields": ("name", "mobile_no", "license_no"),
            "description": "Basic driver details"
        }),
        ("Identity Proof", {
            "fields": ("id_proof_type", "id_proof_number"),
            "classes": ("wide",),
        }),
        ("Photo", {
            "fields": ("photo", "photo_preview_large"),
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

    readonly_fields = (
        "created_by", "created_at", "updated_by", "updated_at",
        "photo_preview_large"
    )

    @admin.display(description="Photo")
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />',
                obj.photo.url
            )
        return format_html(
            '<span style="color: #999; font-size: 10px;">{}</span>',
            "No Photo"
        )

    @admin.display(description="Photo Preview")
    def photo_preview_large(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="150" height="150" style="border-radius: 8px; object-fit: cover;" />',
                obj.photo.url
            )
        return format_html('<span style="color: #999;">{}</span>', "No photo uploaded")

    @admin.display(description="Active", boolean=True, ordering="is_active")
    def is_active_display(self, obj):
        return obj.is_active

    @admin.display(description="Gate Entries")
    def gate_entry_count(self, obj):
        count = obj.gate_entries.count()
        if count > 0:
            return format_html(
                '<a href="{}?driver__id__exact={}" style="color: green; font-weight: bold;">{}</a>',
                reverse('admin:driver_management_vehicleentry_changelist'),
                obj.id,
                count
            )
        return format_html('<span style="color: #999;">{}</span>', "0")

    # Admin actions
    @admin.action(description="Activate selected drivers")
    def activate_drivers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} driver(s) activated.")

    @admin.action(description="Deactivate selected drivers")
    def deactivate_drivers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} driver(s) deactivated.")

    actions = ["activate_drivers", "deactivate_drivers"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'gate_entries'
        ).select_related('created_by', 'updated_by')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(VehicleEntry)
class VehicleEntryAdmin(admin.ModelAdmin):
    """
    Comprehensive Vehicle Entry (Gate Entry) Admin with all features
    """
    list_display = (
        "entry_no",
        "company",
        "vehicle_link",
        "driver_link",
        "entry_type_badge",
        "status_badge",
        "is_locked_display",
        "entry_time",
        "has_security_check",
        "has_weighment",
    )
    list_display_links = ("entry_no",)
    list_filter = (
        "company",
        "entry_type",
        "status",
        "is_locked",
        "entry_time",
        "created_at",
    )
    search_fields = (
        "entry_no",
        "vehicle__vehicle_number",
        "driver__name",
        "driver__mobile_no",
        "driver__license_no",
        "remarks",
    )
    ordering = ("-entry_time",)
    date_hierarchy = "entry_time"
    list_per_page = 25

    autocomplete_fields = ["company", "vehicle", "driver"]

    fieldsets = (
        ("Entry Information", {
            "fields": ("entry_no", "company", "entry_type"),
            "description": "Gate entry details"
        }),
        ("Vehicle & Driver", {
            "fields": ("vehicle", "driver"),
            "classes": ("wide",),
        }),
        ("Status", {
            "fields": ("status", "is_locked"),
        }),
        ("Additional Information", {
            "fields": ("remarks",),
        }),
        ("Timestamps", {
            "fields": ("entry_time", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
        ("Audit", {
            "fields": ("created_by", "updated_by"),
            "classes": ("collapse",),
        }),
    )

    readonly_fields = (
        "entry_no", "entry_time", "created_at", "updated_at",
        "created_by", "updated_by"
    )

    @admin.display(description="Vehicle", ordering="vehicle__vehicle_number")
    def vehicle_link(self, obj):
        url = reverse('admin:vehicle_management_vehicle_change', args=[obj.vehicle.id])
        return format_html('<a href="{}">{}</a>', url, obj.vehicle.vehicle_number)

    @admin.display(description="Driver", ordering="driver__name")
    def driver_link(self, obj):
        url = reverse('admin:driver_management_driver_change', args=[obj.driver.id])
        return format_html('<a href="{}">{}</a>', url, obj.driver.name)

    @admin.display(description="Entry Type", ordering="entry_type")
    def entry_type_badge(self, obj):
        colors = {
            "RAW_MATERIAL": "#3498db",
            "DAILY_NEED": "#27ae60",
            "MAINTENANCE": "#f39c12",
            "CONSTRUCTION": "#9b59b6",
        }
        color = colors.get(obj.entry_type, "#95a5a6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_entry_type_display()
        )

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        colors = {
            "DRAFT": "#95a5a6",
            "IN_PROGRESS": "#3498db",
            "QC_PENDING": "#f39c12",
            "QC_COMPLETED": "#27ae60",
            "COMPLETED": "#2ecc71",
            "CANCELLED": "#e74c3c",
        }
        color = colors.get(obj.status, "#95a5a6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )

    @admin.display(description="Locked", boolean=True, ordering="is_locked")
    def is_locked_display(self, obj):
        return obj.is_locked

    @admin.display(description="Security", boolean=True)
    def has_security_check(self, obj):
        return hasattr(obj, 'security_check')

    @admin.display(description="Weighment", boolean=True)
    def has_weighment(self, obj):
        return hasattr(obj, 'weighment')

    # Admin actions
    @admin.action(description="Mark selected as In Progress")
    def mark_in_progress(self, request, queryset):
        updated = queryset.filter(is_locked=False).update(status="IN_PROGRESS")
        self.message_user(request, f"{updated} entry(s) marked as In Progress.")

    @admin.action(description="Mark selected as Completed")
    def mark_completed(self, request, queryset):
        updated = queryset.filter(is_locked=False).update(status="COMPLETED")
        self.message_user(request, f"{updated} entry(s) marked as Completed.")

    @admin.action(description="Cancel selected entries")
    def cancel_entries(self, request, queryset):
        updated = queryset.filter(is_locked=False).update(status="CANCELLED")
        self.message_user(request, f"{updated} entry(s) cancelled.")

    @admin.action(description="Lock selected entries")
    def lock_entries(self, request, queryset):
        updated = queryset.update(is_locked=True)
        self.message_user(request, f"{updated} entry(s) locked.")

    @admin.action(description="Unlock selected entries")
    def unlock_entries(self, request, queryset):
        updated = queryset.update(is_locked=False)
        self.message_user(request, f"{updated} entry(s) unlocked.")

    actions = [
        "mark_in_progress", "mark_completed", "cancel_entries",
        "lock_entries", "unlock_entries"
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'company', 'vehicle', 'driver', 'created_by', 'updated_by'
        ).prefetch_related('security_check', 'weighment')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
