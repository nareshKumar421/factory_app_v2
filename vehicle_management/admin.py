# vehicle_management/admin.py
"""
Enhanced Vehicle Management Admin Configuration for Factory Jivo Wellness
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Transporter, Vehicle


class VehicleInline(admin.TabularInline):
    """Inline for showing vehicles belonging to a transporter"""
    model = Vehicle
    extra = 0
    fields = ("vehicle_number", "vehicle_type", "capacity_ton", "is_active")
    readonly_fields = ("vehicle_number",)
    show_change_link = True


@admin.register(Transporter)
class TransporterAdmin(admin.ModelAdmin):
    """
    Comprehensive Transporter Admin with all features
    """
    list_display = (
        "name",
        "contact_person",
        "mobile_no",
        "vehicle_count",
        "is_active_display",
        "created_at",
    )
    list_display_links = ("name",)
    list_filter = (
        "is_active",
        "created_at",
    )
    search_fields = (
        "name",
        "contact_person",
        "mobile_no",
    )
    ordering = ("name",)
    date_hierarchy = "created_at"
    list_per_page = 25

    inlines = [VehicleInline]

    fieldsets = (
        ("Transporter Information", {
            "fields": ("name",),
            "description": "Transporter/Logistics company details"
        }),
        ("Contact Information", {
            "fields": ("contact_person", "mobile_no"),
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

    @admin.display(description="Active", boolean=True, ordering="is_active")
    def is_active_display(self, obj):
        return obj.is_active

    @admin.display(description="Vehicles")
    def vehicle_count(self, obj):
        count = obj.vehicle_set.filter(is_active=True).count()
        if count > 0:
            return format_html(
                '<a href="{}?transporter__id__exact={}" style="color: green; font-weight: bold;">{}</a>',
                reverse('admin:vehicle_management_vehicle_changelist'),
                obj.id,
                count
            )
        return format_html('<span style="color: #999;">{}</span>', "0")

    # Admin actions
    @admin.action(description="Activate selected transporters")
    def activate_transporters(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} transporter(s) activated.")

    @admin.action(description="Deactivate selected transporters")
    def deactivate_transporters(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} transporter(s) deactivated.")

    actions = ["activate_transporters", "deactivate_transporters"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'vehicle_set'
        ).select_related('created_by', 'updated_by')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """
    Comprehensive Vehicle Admin with all features
    """
    list_display = (
        "vehicle_number",
        "vehicle_type_badge",
        "transporter_link",
        "capacity_display",
        "is_active_display",
        "gate_entry_count",
        "created_at",
    )
    list_display_links = ("vehicle_number",)
    list_filter = (
        "vehicle_type",
        "transporter",
        "is_active",
        "created_at",
    )
    search_fields = (
        "vehicle_number",
        "transporter__name",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 25

    autocomplete_fields = ["transporter"]

    fieldsets = (
        ("Vehicle Information", {
            "fields": ("vehicle_number", "vehicle_type"),
            "description": "Basic vehicle details"
        }),
        ("Specifications", {
            "fields": ("capacity_ton",),
            "classes": ("wide",),
        }),
        ("Transporter", {
            "fields": ("transporter",),
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

    @admin.display(description="Type", ordering="vehicle_type")
    def vehicle_type_badge(self, obj):
        colors = {
            "TRUCK": "#3498db",
            "TEMPO": "#27ae60",
            "CONTAINER": "#9b59b6",
            "TRACTOR": "#f39c12",
        }
        color = colors.get(obj.vehicle_type, "#95a5a6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_vehicle_type_display()
        )

    @admin.display(description="Transporter", ordering="transporter__name")
    def transporter_link(self, obj):
        if obj.transporter:
            url = reverse('admin:vehicle_management_transporter_change', args=[obj.transporter.id])
            return format_html('<a href="{}">{}</a>', url, obj.transporter.name)
        return format_html('<span style="color: #999;">{}</span>', "Not Assigned")

    @admin.display(description="Capacity (Ton)", ordering="capacity_ton")
    def capacity_display(self, obj):
        if obj.capacity_ton:
            return format_html(
                '<span style="font-weight: bold;">{} T</span>',
                obj.capacity_ton
            )
        return format_html('<span style="color: #999;">{}</span>', "N/A")

    @admin.display(description="Active", boolean=True, ordering="is_active")
    def is_active_display(self, obj):
        return obj.is_active

    @admin.display(description="Gate Entries")
    def gate_entry_count(self, obj):
        count = obj.driver_gate_entries.count()
        if count > 0:
            return format_html(
                '<a href="{}?vehicle__id__exact={}" style="color: green; font-weight: bold;">{}</a>',
                reverse('admin:driver_management_vehicleentry_changelist'),
                obj.id,
                count
            )
        return format_html('<span style="color: #999;">{}</span>', "0")

    # Admin actions
    @admin.action(description="Activate selected vehicles")
    def activate_vehicles(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} vehicle(s) activated.")

    @admin.action(description="Deactivate selected vehicles")
    def deactivate_vehicles(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} vehicle(s) deactivated.")

    @admin.action(description="Mark as Truck")
    def mark_as_truck(self, request, queryset):
        updated = queryset.update(vehicle_type="TRUCK")
        self.message_user(request, f"{updated} vehicle(s) marked as Truck.")

    @admin.action(description="Mark as Tempo")
    def mark_as_tempo(self, request, queryset):
        updated = queryset.update(vehicle_type="TEMPO")
        self.message_user(request, f"{updated} vehicle(s) marked as Tempo.")

    @admin.action(description="Mark as Container")
    def mark_as_container(self, request, queryset):
        updated = queryset.update(vehicle_type="CONTAINER")
        self.message_user(request, f"{updated} vehicle(s) marked as Container.")

    actions = [
        "activate_vehicles", "deactivate_vehicles",
        "mark_as_truck", "mark_as_tempo", "mark_as_container"
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'transporter', 'created_by', 'updated_by'
        ).prefetch_related('driver_gate_entries')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
