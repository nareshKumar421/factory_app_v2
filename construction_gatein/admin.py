from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ConstructionGateEntry, ConstructionMaterialCategory


@admin.register(ConstructionMaterialCategory)
class ConstructionMaterialCategoryAdmin(admin.ModelAdmin):
    """
    Admin for ConstructionMaterialCategory lookup table.
    """
    list_display = (
        "category_name",
        "description",
        "is_active",
        "entry_count",
    )
    list_display_links = ("category_name",)
    list_filter = ("is_active",)
    search_fields = ("category_name", "description")
    ordering = ("category_name",)
    list_per_page = 25

    fieldsets = (
        ("Category Information", {
            "fields": ("category_name", "description", "is_active"),
            "description": "Construction material category configuration"
        }),
    )

    @admin.display(description="Entries")
    def entry_count(self, obj):
        count = obj.construction_entries.count()
        if count > 0:
            return format_html(
                '<a href="{}?material_category__id__exact={}" '
                'style="color: green; font-weight: bold;">{}</a>',
                reverse('admin:construction_gatein_constructiongateentry_changelist'),
                obj.id,
                count
            )
        return format_html('<span style="color: #999;">{}</span>', "0")


@admin.register(ConstructionGateEntry)
class ConstructionGateEntryAdmin(admin.ModelAdmin):
    """
    Comprehensive Construction Gate Entry Admin.
    """
    list_display = (
        "id",
        "work_order_number",
        "vehicle_entry_link",
        "material_category_link",
        "material_description_short",
        "quantity_display",
        "unit_badge",
        "security_approval_badge",
        "contractor_name",
        "site_engineer",
        "created_by_link",
        "created_at",
    )
    list_display_links = ("id", "work_order_number")
    list_filter = (
        "material_category",
        "security_approval",
        "unit",
        "created_at",
    )
    search_fields = (
        "work_order_number",
        "material_description",
        "contractor_name",
        "contractor_contact",
        "project_name",
        "site_engineer",
        "challan_number",
        "invoice_number",
        "vehicle_entry__entry_no",
        "remarks",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 25

    autocomplete_fields = ["material_category"]
    raw_id_fields = ["vehicle_entry"]

    fieldsets = (
        ("Entry Information", {
            "fields": ("vehicle_entry", "material_category", "work_order_number", "project_name"),
            "description": "Link to gate entry and select material category"
        }),
        ("Contractor Details", {
            "fields": (
                "contractor_name",
                "contractor_contact",
            ),
            "classes": ("wide",),
        }),
        ("Material Details", {
            "fields": (
                "material_description",
                ("quantity", "unit"),
            ),
            "classes": ("wide",),
        }),
        ("Documents", {
            "fields": ("challan_number", "invoice_number"),
            "classes": ("wide",),
        }),
        ("Approval Information", {
            "fields": ("site_engineer", "security_approval"),
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

    @admin.display(description="Category", ordering="material_category__category_name")
    def material_category_link(self, obj):
        if obj.material_category:
            url = reverse('admin:construction_gatein_constructionmaterialcategory_change', args=[obj.material_category.id])
            return format_html(
                '<a href="{}" style="color: #3498db;">{}</a>',
                url, obj.material_category.category_name
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
        color = colors.get(obj.unit, "#95a5a6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_unit_display()
        )

    @admin.display(description="Approval", ordering="security_approval")
    def security_approval_badge(self, obj):
        colors = {
            "PENDING": "#f39c12",
            "APPROVED": "#27ae60",
            "REJECTED": "#e74c3c",
        }
        color = colors.get(obj.security_approval, "#95a5a6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_security_approval_display()
        )

    @admin.display(description="Created By", ordering="created_by__full_name")
    def created_by_link(self, obj):
        if obj.created_by:
            url = reverse('admin:accounts_user_change', args=[obj.created_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.created_by.full_name)
        return format_html('<span style="color: #999;">{}</span>', "System")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'vehicle_entry', 'material_category', 'created_by'
        )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
