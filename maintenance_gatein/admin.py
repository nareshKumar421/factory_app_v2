from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import MaintenanceGateEntry, MaintenanceType


@admin.register(MaintenanceType)
class MaintenanceTypeAdmin(admin.ModelAdmin):
    """
    Admin for MaintenanceType lookup table.
    """
    list_display = (
        "type_name",
        "description",
        "is_active",
        "entry_count",
    )
    list_display_links = ("type_name",)
    list_filter = ("is_active",)
    search_fields = ("type_name", "description")
    ordering = ("type_name",)
    list_per_page = 25

    fieldsets = (
        ("Type Information", {
            "fields": ("type_name", "description", "is_active"),
            "description": "Maintenance type configuration"
        }),
    )

    @admin.display(description="Entries")
    def entry_count(self, obj):
        count = obj.maintenance_entries.count()
        if count > 0:
            return format_html(
                '<a href="{}?maintenance_type__id__exact={}" '
                'style="color: green; font-weight: bold;">{}</a>',
                reverse('admin:maintenance_gatein_maintenancegateentry_changelist'),
                obj.id,
                count
            )
        return format_html('<span style="color: #999;">{}</span>', "0")


@admin.register(MaintenanceGateEntry)
class MaintenanceGateEntryAdmin(admin.ModelAdmin):
    """
    Comprehensive Maintenance Gate Entry Admin.
    """
    list_display = (
        "id",
        "work_order_number",
        "vehicle_entry_link",
        "maintenance_type_link",
        "material_description_short",
        "quantity_display",
        "unit_badge",
        "urgency_badge",
        "supplier_name",
        "receiving_department",
        "created_by_link",
        "created_at",
    )
    list_display_links = ("id", "work_order_number")
    list_filter = (
        "maintenance_type",
        "urgency_level",
        "unit",
        "receiving_department",
        "created_at",
    )
    search_fields = (
        "work_order_number",
        "material_description",
        "supplier_name",
        "part_number",
        "invoice_number",
        "equipment_id",
        "vehicle_entry__entry_no",
        "remarks",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 25

    autocomplete_fields = ["maintenance_type"]
    raw_id_fields = ["vehicle_entry"]

    fieldsets = (
        ("Entry Information", {
            "fields": ("vehicle_entry", "maintenance_type", "work_order_number"),
            "description": "Link to gate entry and select maintenance type"
        }),
        ("Material Details", {
            "fields": (
                "supplier_name",
                "material_description",
                "part_number",
                ("quantity", "unit"),
            ),
            "classes": ("wide",),
        }),
        ("Equipment & Department", {
            "fields": ("equipment_id", "receiving_department", "urgency_level"),
        }),
        ("Documents", {
            "fields": ("invoice_number",),
            "classes": ("wide",),
        }),
        ("Additional Information", {
            "fields": ("remarks",),
        }),
        ("Audit Information", {
            "fields": ("created_by", "created_at", "inward_time"),
            "classes": ("collapse",),
        }),
    )

    readonly_fields = ("created_at", "created_by", "vehicle_entry", "inward_time", "work_order_number")

    @admin.display(description="Gate Entry", ordering="vehicle_entry__entry_no")
    def vehicle_entry_link(self, obj):
        if obj.vehicle_entry:
            url = reverse('admin:driver_management_vehicleentry_change', args=[obj.vehicle_entry.id])
            return format_html(
                '<a href="{}" style="font-weight: bold;">{}</a>',
                url, obj.vehicle_entry.entry_no
            )
        return format_html('<span style="color: #999;">{}</span>', "-")

    @admin.display(description="Type", ordering="maintenance_type__type_name")
    def maintenance_type_link(self, obj):
        if obj.maintenance_type:
            url = reverse('admin:maintenance_gatein_maintenancetype_change', args=[obj.maintenance_type.id])
            return format_html(
                '<a href="{}" style="color: #3498db;">{}</a>',
                url, obj.maintenance_type.type_name
            )
        return format_html('<span style="color: #999;">{}</span>', "Unspecified")

    @admin.display(description="Material")
    def material_description_short(self, obj):
        desc = obj.material_description[:40]
        if len(obj.material_description) > 40:
            desc += "..."
        return desc

    @admin.display(description="Quantity", ordering="quantity")
    def quantity_display(self, obj):
        return format_html(
            '<span style="color: #27ae60; font-weight: bold;">{}</span>',
            f"{obj.quantity:,.2f}"
        )

    @admin.display(description="Unit", ordering="unit")
    def unit_badge(self, obj):
        colors = {
            "PCS": "#3498db",
            "KG": "#27ae60",
            "LTR": "#9b59b6",
            "BOX": "#f39c12",
        }
        unit_name = str(obj.unit) if obj.unit else "-"
        color = colors.get(unit_name.upper(), "#95a5a6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, unit_name
        )

    @admin.display(description="Urgency", ordering="urgency_level")
    def urgency_badge(self, obj):
        colors = {
            "NORMAL": "#27ae60",
            "HIGH": "#f39c12",
            "CRITICAL": "#e74c3c",
        }
        color = colors.get(obj.urgency_level, "#95a5a6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_urgency_level_display()
        )

    @admin.display(description="Created By", ordering="created_by__full_name")
    def created_by_link(self, obj):
        if obj.created_by:
            url = reverse('admin:accounts_user_change', args=[obj.created_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.created_by.full_name)
        return format_html('<span style="color: #999;">{}</span>', "System")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'vehicle_entry', 'maintenance_type', 'created_by', 'receiving_department'
        )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
