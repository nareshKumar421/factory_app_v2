# daily_needs_gatein/admin.py
"""
Enhanced Daily Needs Gate-In Admin Configuration for Factory Jivo Wellness
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Count
from .models import DailyNeedGateEntry, CategoryList


@admin.register(CategoryList)
class CategoryListAdmin(admin.ModelAdmin):
    """
    Comprehensive Category List Admin
    """
    list_display = (
        "category_name",
        "entry_count",
        "total_quantity",
    )
    list_display_links = ("category_name",)
    search_fields = ("category_name",)
    ordering = ("category_name",)
    list_per_page = 25

    fieldsets = (
        ("Category Information", {
            "fields": ("category_name",),
            "description": "Daily needs category name"
        }),
    )

    @admin.display(description="Entries")
    def entry_count(self, obj):
        count = obj.daily_need_entries.count()
        if count > 0:
            return format_html(
                '<a href="{}?item_category__id__exact={}" '
                'style="color: green; font-weight: bold;">{}</a>',
                reverse('admin:daily_needs_gatein_dailyneedgateentry_changelist'),
                obj.id,
                count
            )
        return format_html('<span style="color: #999;">{}</span>', "0")

    @admin.display(description="Total Qty")
    def total_quantity(self, obj):
        total = obj.daily_need_entries.aggregate(total=Sum('quantity'))['total']
        if total:
            return format_html(
                '<span style="font-weight: bold;">{}</span>',
                f"{total:,.2f}"
            )
        return format_html('<span style="color: #999;">{}</span>', "0.00")

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('daily_need_entries')


@admin.register(DailyNeedGateEntry)
class DailyNeedGateEntryAdmin(admin.ModelAdmin):
    """
    Comprehensive Daily Need Gate Entry Admin with all features
    """
    list_display = (
        "id",
        "vehicle_entry_link",
        "material_name",
        "item_category_link",
        "quantity_display",
        "unit_badge",
        "supplier_name",
        "receiving_department",
        "bill_number",
        "created_by_link",
        "created_at",
    )
    list_display_links = ("id", "material_name")
    list_filter = (
        "item_category",
        "unit",
        "receiving_department",
        "created_at",
    )
    search_fields = (
        "material_name",
        "supplier_name",
        "bill_number",
        "delivery_challan_number",
        "receiving_department",
        "canteen_supervisor",
        "vehicle_or_person_name",
        "contact_number",
        "vehicle_entry__entry_no",
        "remarks",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 25

    autocomplete_fields = ["item_category"]
    raw_id_fields = ["vehicle_entry"]

    fieldsets = (
        ("Entry Information", {
            "fields": ("vehicle_entry", "item_category"),
            "description": "Link to gate entry and select category"
        }),
        ("Material Details", {
            "fields": (
                "supplier_name",
                "material_name",
                ("quantity", "unit"),
            ),
            "classes": ("wide",),
        }),
        ("Department", {
            "fields": ("receiving_department",),
        }),
        ("Documents", {
            "fields": ("bill_number", "delivery_challan_number"),
            "classes": ("wide",),
        }),
        ("Contact Information", {
            "fields": (
                "canteen_supervisor",
                "vehicle_or_person_name",
                "contact_number",
            ),
            "classes": ("wide",),
        }),
        ("Additional Information", {
            "fields": ("remarks",),
        }),
        ("Audit Information", {
            "fields": ("created_by", "created_at"),
            "classes": ("collapse",),
        }),
    )

    readonly_fields = ("created_at", "created_by", "vehicle_entry")

    @admin.display(description="Gate Entry", ordering="vehicle_entry__entry_no")
    def vehicle_entry_link(self, obj):
        if obj.vehicle_entry:
            url = reverse('admin:driver_management_vehicleentry_change', args=[obj.vehicle_entry.id])
            return format_html(
                '<a href="{}" style="font-weight: bold;">{}</a>',
                url, obj.vehicle_entry.entry_no
            )
        return format_html('<span style="color: #999;">{}</span>', "-")

    @admin.display(description="Category", ordering="item_category__category_name")
    def item_category_link(self, obj):
        if obj.item_category:
            url = reverse('admin:daily_needs_gatein_categorylist_change', args=[obj.item_category.id])
            return format_html(
                '<a href="{}" style="color: #3498db;">{}</a>',
                url, obj.item_category.category_name
            )
        return format_html('<span style="color: #999;">{}</span>', "Uncategorized")

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

    @admin.display(description="Created By", ordering="created_by__full_name")
    def created_by_link(self, obj):
        if obj.created_by:
            url = reverse('admin:accounts_user_change', args=[obj.created_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.created_by.full_name)
        return format_html('<span style="color: #999;">{}</span>', "System")

    # Admin actions
    @admin.action(description="Change unit to Pieces (PCS)")
    def change_to_pcs(self, request, queryset):
        updated = queryset.update(unit="PCS")
        self.message_user(request, f"{updated} entry(s) changed to Pieces.")

    @admin.action(description="Change unit to Kilogram (KG)")
    def change_to_kg(self, request, queryset):
        updated = queryset.update(unit="KG")
        self.message_user(request, f"{updated} entry(s) changed to Kilogram.")

    @admin.action(description="Change unit to Litre (LTR)")
    def change_to_ltr(self, request, queryset):
        updated = queryset.update(unit="LTR")
        self.message_user(request, f"{updated} entry(s) changed to Litre.")

    @admin.action(description="Change unit to Box (BOX)")
    def change_to_box(self, request, queryset):
        updated = queryset.update(unit="BOX")
        self.message_user(request, f"{updated} entry(s) changed to Box.")

    @admin.action(description="Set receiving department to Canteen")
    def set_dept_canteen(self, request, queryset):
        updated = queryset.update(receiving_department="Canteen")
        self.message_user(request, f"{updated} entry(s) set to Canteen department.")

    @admin.action(description="Set receiving department to Store")
    def set_dept_store(self, request, queryset):
        updated = queryset.update(receiving_department="Store")
        self.message_user(request, f"{updated} entry(s) set to Store department.")

    @admin.action(description="Set receiving department to Production")
    def set_dept_production(self, request, queryset):
        updated = queryset.update(receiving_department="Production")
        self.message_user(request, f"{updated} entry(s) set to Production department.")

    @admin.action(description="Clear bill number")
    def clear_bill_number(self, request, queryset):
        updated = queryset.update(bill_number="")
        self.message_user(request, f"{updated} entry(s) bill number cleared.")

    @admin.action(description="Duplicate selected entries")
    def duplicate_entries(self, request, queryset):
        for entry in queryset:
            entry.pk = None
            entry.bill_number = ""
            entry.delivery_challan_number = ""
            entry.vehicle_entry = None
            entry.save()
        self.message_user(request, f"{queryset.count()} entry(s) duplicated.")

    actions = [
        "change_to_pcs", "change_to_kg", "change_to_ltr", "change_to_box",
        "set_dept_canteen", "set_dept_store", "set_dept_production",
        "clear_bill_number", "duplicate_entries"
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'vehicle_entry', 'item_category', 'created_by'
        )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
