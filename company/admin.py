# company/admin.py
"""
Enhanced Company Admin Configuration for Factory Jivo Wellness
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Company, UserCompany, UserRole


class UserCompanyInline(admin.TabularInline):
    """Inline for showing users assigned to a company"""
    model = UserCompany
    extra = 0
    autocomplete_fields = ["user", "role"]
    readonly_fields = ("get_user_email",)
    fields = ("user", "get_user_email", "role", "is_default", "is_active")

    @admin.display(description="User Email")
    def get_user_email(self, obj):
        if obj.user:
            return obj.user.email
        return "-"


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Enhanced Company Admin with comprehensive features
    """
    list_display = (
        "name",
        "code",
        "is_active_display",
        "user_count",
        "entry_count",
    )
    list_display_links = ("name", "code")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    ordering = ("name",)

    list_editable = ("is_active_display",)
    list_per_page = 25

    inlines = [UserCompanyInline]

    fieldsets = (
        ("Company Information", {
            "fields": ("name", "code"),
            "description": "Basic company details"
        }),
        ("Status", {
            "fields": ("is_active",),
        }),
    )

    @admin.display(description="Active", boolean=True, ordering="is_active")
    def is_active_display(self, obj):
        return obj.is_active

    # Fix: Remove the duplicate setter method since list_editable doesn't work this way
    # Instead, just use 'is_active' directly in list_editable

    @admin.display(description="Users")
    def user_count(self, obj):
        count = obj.usercompany_set.filter(is_active=True).count()
        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>',
                count
            )
        return format_html('<span style="color: #999;">{}</span>', "0")

    @admin.display(description="Gate Entries")
    def entry_count(self, obj):
        count = obj.driver_vehicle_entries.count()
        return count

    # Admin actions
    @admin.action(description="Activate selected companies")
    def activate_companies(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} company(s) activated.")

    @admin.action(description="Deactivate selected companies")
    def deactivate_companies(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} company(s) deactivated.")

    actions = ["activate_companies", "deactivate_companies"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'usercompany_set',
            'driver_vehicle_entries'
        )


# Re-register with correct list_editable
CompanyAdmin.list_editable = ()


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """
    Enhanced User Role Admin
    """
    list_display = ("name", "description", "user_count")
    search_fields = ("name", "description")
    ordering = ("name",)
    list_per_page = 25

    fieldsets = (
        ("Role Information", {
            "fields": ("name", "description"),
            "description": "Define organizational roles"
        }),
    )

    @admin.display(description="Assigned Users")
    def user_count(self, obj):
        count = obj.usercompany_set.filter(is_active=True).count()
        return count

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('usercompany_set')


@admin.register(UserCompany)
class UserCompanyAdmin(admin.ModelAdmin):
    """
    Enhanced User-Company Assignment Admin
    """
    list_display = (
        "user",
        "get_user_email",
        "company",
        "role",
        "is_default_display",
        "is_active_display",
    )
    list_display_links = ("user",)
    list_filter = (
        "company",
        "role",
        "is_default",
        "is_active",
    )
    search_fields = (
        "user__email",
        "user__full_name",
        "user__employee_code",
        "company__name",
        "company__code",
    )
    ordering = ("company", "user")
    list_per_page = 25

    autocomplete_fields = ["user", "company", "role"]

    fieldsets = (
        ("Assignment", {
            "fields": ("user", "company", "role"),
            "description": "Assign user to company with role"
        }),
        ("Settings", {
            "fields": ("is_default", "is_active"),
        }),
    )

    @admin.display(description="User Email", ordering="user__email")
    def get_user_email(self, obj):
        return obj.user.email

    @admin.display(description="Default", boolean=True, ordering="is_default")
    def is_default_display(self, obj):
        return obj.is_default

    @admin.display(description="Active", boolean=True, ordering="is_active")
    def is_active_display(self, obj):
        return obj.is_active

    # Admin actions
    @admin.action(description="Set as default company for user")
    def set_default(self, request, queryset):
        for uc in queryset:
            UserCompany.objects.filter(user=uc.user).update(is_default=False)
            uc.is_default = True
            uc.save()
        self.message_user(request, f"Updated {queryset.count()} assignment(s) as default.")

    @admin.action(description="Activate selected assignments")
    def activate_assignments(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} assignment(s) activated.")

    @admin.action(description="Deactivate selected assignments")
    def deactivate_assignments(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} assignment(s) deactivated.")

    actions = ["set_default", "activate_assignments", "deactivate_assignments"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'company', 'role'
        )
