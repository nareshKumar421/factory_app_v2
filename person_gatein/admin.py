from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from datetime import timedelta
from .models import PersonType, Gate, Contractor, Visitor, Labour, EntryLog


# =========================================
# Custom Filters
# =========================================

class ExpiredContractFilter(admin.SimpleListFilter):
    title = 'Contract Status'
    parameter_name = 'contract_status'

    def lookups(self, request, model_admin):
        return (
            ('valid', 'Valid Contract'),
            ('expired', 'Expired Contract'),
            ('expiring_soon', 'Expiring in 30 days'),
        )

    def queryset(self, request, queryset):
        today = timezone.now().date()
        if self.value() == 'valid':
            return queryset.filter(contract_valid_till__gte=today)
        if self.value() == 'expired':
            return queryset.filter(contract_valid_till__lt=today)
        if self.value() == 'expiring_soon':
            return queryset.filter(
                contract_valid_till__gte=today,
                contract_valid_till__lte=today + timedelta(days=30)
            )


class PermitStatusFilter(admin.SimpleListFilter):
    title = 'Permit Status'
    parameter_name = 'permit_status'

    def lookups(self, request, model_admin):
        return (
            ('valid', 'Valid Permit'),
            ('expired', 'Expired Permit'),
            ('expiring_soon', 'Expiring in 7 days'),
            ('no_permit', 'No Permit Date'),
        )

    def queryset(self, request, queryset):
        today = timezone.now().date()
        if self.value() == 'valid':
            return queryset.filter(permit_valid_till__gte=today)
        if self.value() == 'expired':
            return queryset.filter(permit_valid_till__lt=today)
        if self.value() == 'expiring_soon':
            return queryset.filter(
                permit_valid_till__gte=today,
                permit_valid_till__lte=today + timedelta(days=7)
            )
        if self.value() == 'no_permit':
            return queryset.filter(permit_valid_till__isnull=True)


class EntryDurationFilter(admin.SimpleListFilter):
    title = 'Duration Inside'
    parameter_name = 'duration'

    def lookups(self, request, model_admin):
        return (
            ('short', 'Less than 1 hour'),
            ('medium', '1-4 hours'),
            ('long', '4-8 hours'),
            ('extended', 'More than 8 hours'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'short':
            return queryset.filter(
                status='IN',
                entry_time__gte=now - timedelta(hours=1)
            )
        if self.value() == 'medium':
            return queryset.filter(
                status='IN',
                entry_time__lt=now - timedelta(hours=1),
                entry_time__gte=now - timedelta(hours=4)
            )
        if self.value() == 'long':
            return queryset.filter(
                status='IN',
                entry_time__lt=now - timedelta(hours=4),
                entry_time__gte=now - timedelta(hours=8)
            )
        if self.value() == 'extended':
            return queryset.filter(
                status='IN',
                entry_time__lt=now - timedelta(hours=8)
            )


class TodayEntryFilter(admin.SimpleListFilter):
    title = 'Quick Filter'
    parameter_name = 'quick'

    def lookups(self, request, model_admin):
        return (
            ('today', "Today's Entries"),
            ('yesterday', "Yesterday's Entries"),
            ('this_week', 'This Week'),
            ('inside_now', 'Currently Inside'),
        )

    def queryset(self, request, queryset):
        today = timezone.now().date()
        if self.value() == 'today':
            return queryset.filter(entry_time__date=today)
        if self.value() == 'yesterday':
            return queryset.filter(entry_time__date=today - timedelta(days=1))
        if self.value() == 'this_week':
            return queryset.filter(entry_time__date__gte=today - timedelta(days=7))
        if self.value() == 'inside_now':
            return queryset.filter(status='IN')


# =========================================
# Inline Models
# =========================================

class LabourInline(admin.TabularInline):
    model = Labour
    extra = 0
    fields = ('name', 'mobile', 'skill_type', 'permit_valid_till', 'is_active')
    readonly_fields = ('name',)
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


class EntryLogInline(admin.TabularInline):
    model = EntryLog
    extra = 0
    fk_name = 'visitor'
    fields = ('entry_time', 'gate_in', 'status', 'exit_time', 'purpose')
    readonly_fields = ('entry_time', 'gate_in', 'status', 'exit_time', 'purpose')
    ordering = ('-entry_time',)
    max_num = 10

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class LabourEntryLogInline(admin.TabularInline):
    model = EntryLog
    extra = 0
    fk_name = 'labour'
    fields = ('entry_time', 'gate_in', 'status', 'exit_time', 'purpose')
    readonly_fields = ('entry_time', 'gate_in', 'status', 'exit_time', 'purpose')
    ordering = ('-entry_time',)
    max_num = 10
    verbose_name = "Entry Log"
    verbose_name_plural = "Entry History"

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# =========================================
# Admin Classes
# =========================================

@admin.register(PersonType)
class PersonTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status_badge", "entry_count")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_editable = ("name",)
    ordering = ("name",)

    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">{}</span>', "ACTIVE"
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>', "INACTIVE"
        )
    status_badge.short_description = "Status"

    def entry_count(self, obj):
        count = EntryLog.objects.filter(person_type=obj).count()
        return format_html('<strong>{}</strong>', count)
    entry_count.short_description = "Total Entries"


@admin.register(Gate)
class GateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "location", "status_badge", "entries_in_count", "entries_out_count", "currently_inside")
    list_filter = ("is_active",)
    search_fields = ("name", "location")
    list_editable = ("location",)
    ordering = ("name",)

    actions = ['activate_gates', 'deactivate_gates']

    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">{}</span>', "ACTIVE"
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>', "INACTIVE"
        )
    status_badge.short_description = "Status"

    def entries_in_count(self, obj):
        count = obj.entries_in.count()
        return format_html('<span style="color: #007bff; font-weight: bold;">{}</span>', count)
    entries_in_count.short_description = "Entries In"

    def entries_out_count(self, obj):
        count = obj.entries_out.count()
        return format_html('<span style="color: #6c757d; font-weight: bold;">{}</span>', count)
    entries_out_count.short_description = "Entries Out"

    def currently_inside(self, obj):
        count = obj.entries_in.filter(status='IN').count()
        if count > 0:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 2px 8px; '
                'border-radius: 3px; font-weight: bold;">{}</span>', count
            )
        return format_html('<span style="color: #6c757d;">{}</span>', 0)
    currently_inside.short_description = "Inside Now"

    @admin.action(description="Activate selected gates")
    def activate_gates(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} gate(s) activated.")

    @admin.action(description="Deactivate selected gates")
    def deactivate_gates(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} gate(s) deactivated.")


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = (
        "id", "contractor_name", "contact_person", "mobile_link",
        "contract_status_badge", "labour_count", "status_badge"
    )
    list_filter = ("is_active", ExpiredContractFilter)
    search_fields = ("contractor_name", "contact_person", "mobile")
    date_hierarchy = "contract_valid_till"
    ordering = ("-contract_valid_till",)
    list_per_page = 25

    inlines = [LabourInline]
    actions = ['activate_contractors', 'deactivate_contractors']

    fieldsets = (
        ("Basic Information", {
            "fields": ("contractor_name", "contact_person", "mobile")
        }),
        ("Address", {
            "fields": ("address",),
            "classes": ("collapse",)
        }),
        ("Contract Details", {
            "fields": ("contract_valid_till", "is_active")
        }),
    )

    def mobile_link(self, obj):
        if obj.mobile:
            return format_html('<a href="tel:{}">{}</a>', obj.mobile, obj.mobile)
        return "-"
    mobile_link.short_description = "Mobile"

    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">{}</span>', "ACTIVE"
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>', "INACTIVE"
        )
    status_badge.short_description = "Status"

    def contract_status_badge(self, obj):
        if not obj.contract_valid_till:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">{}</span>', "NO DATE"
            )

        today = timezone.now().date()
        days_left = (obj.contract_valid_till - today).days

        if days_left < 0:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">EXPIRED ({}d ago)</span>',
                abs(days_left)
            )
        elif days_left <= 30:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">EXPIRING ({}d left)</span>',
                days_left
            )
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">VALID ({}d left)</span>',
            days_left
        )
    contract_status_badge.short_description = "Contract"

    def labour_count(self, obj):
        total = obj.labours.count()
        active = obj.labours.filter(is_active=True).count()
        return format_html(
            '<span title="Active / Total"><strong>{}</strong> / {}</span>',
            active, total
        )
    labour_count.short_description = "Labours"

    @admin.action(description="Activate selected contractors")
    def activate_contractors(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} contractor(s) activated.")

    @admin.action(description="Deactivate selected contractors")
    def deactivate_contractors(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} contractor(s) deactivated.")


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = (
        "id", "photo_thumbnail", "name", "mobile_link", "company_name",
        "id_proof_display", "blacklist_badge", "visit_count", "last_visit", "created_at"
    )
    list_filter = ("blacklisted", "id_proof_type", "created_at")
    search_fields = ("name", "mobile", "company_name", "id_proof_no")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "photo_preview", "visit_stats")
    list_per_page = 25
    ordering = ("-created_at",)

    inlines = [EntryLogInline]
    actions = ['blacklist_visitors', 'remove_blacklist']

    fieldsets = (
        ("Personal Information", {
            "fields": ("name", "mobile", "company_name")
        }),
        ("Photo", {
            "fields": ("photo", "photo_preview"),
        }),
        ("Identification", {
            "fields": ("id_proof_type", "id_proof_no")
        }),
        ("Status & Stats", {
            "fields": ("blacklisted", "visit_stats", "created_at")
        }),
    )

    def photo_thumbnail(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />',
                obj.photo.url
            )
        return format_html(
            '<span style="display: inline-block; width: 40px; height: 40px; '
            'background-color: #e9ecef; border-radius: 50%; text-align: center; '
            'line-height: 40px; color: #6c757d;">{}</span>', "?"
        )
    photo_thumbnail.short_description = "Photo"

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px;" />',
                obj.photo.url
            )
        return "No photo uploaded"
    photo_preview.short_description = "Photo Preview"

    def mobile_link(self, obj):
        if obj.mobile:
            return format_html('<a href="tel:{}">{}</a>', obj.mobile, obj.mobile)
        return "-"
    mobile_link.short_description = "Mobile"

    def id_proof_display(self, obj):
        if obj.id_proof_type and obj.id_proof_no:
            return format_html(
                '<span title="{}: {}">{}: {}...</span>',
                obj.id_proof_type, obj.id_proof_no,
                obj.id_proof_type, obj.id_proof_no[:8]
            )
        return "-"
    id_proof_display.short_description = "ID Proof"

    def blacklist_badge(self, obj):
        if obj.blacklisted:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>', "BLACKLISTED"
            )
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>', "CLEAR"
        )
    blacklist_badge.short_description = "Status"

    def visit_count(self, obj):
        count = EntryLog.objects.filter(visitor=obj).count()
        inside = EntryLog.objects.filter(visitor=obj, status='IN').exists()
        if inside:
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 2px 8px; '
                'border-radius: 3px;">{} (INSIDE)</span>', count
            )
        return count
    visit_count.short_description = "Visits"

    def last_visit(self, obj):
        last_entry = EntryLog.objects.filter(visitor=obj).order_by('-entry_time').first()
        if last_entry:
            return last_entry.entry_time.strftime("%d %b %Y %H:%M")
        return "-"
    last_visit.short_description = "Last Visit"

    def visit_stats(self, obj):
        total = EntryLog.objects.filter(visitor=obj).count()
        inside = EntryLog.objects.filter(visitor=obj, status='IN').count()
        return format_html(
            '<strong>Total Visits:</strong> {} | <strong>Currently Inside:</strong> {}',
            total, inside
        )
    visit_stats.short_description = "Visit Statistics"

    @admin.action(description="Blacklist selected visitors")
    def blacklist_visitors(self, request, queryset):
        updated = queryset.update(blacklisted=True)
        self.message_user(request, f"{updated} visitor(s) blacklisted.")

    @admin.action(description="Remove from blacklist")
    def remove_blacklist(self, request, queryset):
        updated = queryset.update(blacklisted=False)
        self.message_user(request, f"{updated} visitor(s) removed from blacklist.")


@admin.register(Labour)
class LabourAdmin(admin.ModelAdmin):
    list_display = (
        "id", "photo_thumbnail", "name", "contractor_link", "mobile_link",
        "skill_badge", "permit_status_badge", "status_badge", "entry_count"
    )
    list_filter = ("is_active", "contractor", "skill_type", PermitStatusFilter)
    search_fields = ("name", "mobile", "id_proof_no", "contractor__contractor_name")
    autocomplete_fields = ("contractor",)
    list_per_page = 25
    ordering = ("-id",)

    inlines = [LabourEntryLogInline]
    actions = ['activate_labours', 'deactivate_labours']

    fieldsets = (
        ("Personal Information", {
            "fields": ("name", "mobile", "contractor")
        }),
        ("Photo", {
            "fields": ("photo", "photo_preview"),
        }),
        ("Work Details", {
            "fields": ("skill_type", "id_proof_no")
        }),
        ("Permit & Status", {
            "fields": ("permit_valid_till", "is_active")
        }),
    )

    readonly_fields = ("photo_preview",)

    def photo_thumbnail(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />',
                obj.photo.url
            )
        return format_html(
            '<span style="display: inline-block; width: 40px; height: 40px; '
            'background-color: #e9ecef; border-radius: 50%; text-align: center; '
            'line-height: 40px; color: #6c757d;">{}</span>', "?"
        )
    photo_thumbnail.short_description = "Photo"

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px;" />',
                obj.photo.url
            )
        return "No photo uploaded"
    photo_preview.short_description = "Photo Preview"

    def contractor_link(self, obj):
        url = reverse('admin:person_gatein_contractor_change', args=[obj.contractor.id])
        return format_html('<a href="{}">{}</a>', url, obj.contractor.contractor_name)
    contractor_link.short_description = "Contractor"

    def mobile_link(self, obj):
        if obj.mobile:
            return format_html('<a href="tel:{}">{}</a>', obj.mobile, obj.mobile)
        return "-"
    mobile_link.short_description = "Mobile"

    def skill_badge(self, obj):
        if obj.skill_type:
            colors = {
                'electrician': '#007bff',
                'plumber': '#17a2b8',
                'carpenter': '#28a745',
                'mason': '#ffc107',
                'helper': '#6c757d',
                'welder': '#dc3545',
            }
            color = colors.get(obj.skill_type.lower(), '#6c757d')
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">{}</span>',
                color, obj.skill_type.upper()
            )
        return "-"
    skill_badge.short_description = "Skill"

    def permit_status_badge(self, obj):
        if not obj.permit_valid_till:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">{}</span>', "NO PERMIT"
            )

        today = timezone.now().date()
        days_left = (obj.permit_valid_till - today).days

        if days_left < 0:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">{}</span>', "EXPIRED"
            )
        elif days_left <= 7:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">{}d LEFT</span>',
                days_left
            )
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>', "VALID"
        )
    permit_status_badge.short_description = "Permit"

    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">{}</span>', "ACTIVE"
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>', "INACTIVE"
        )
    status_badge.short_description = "Status"

    def entry_count(self, obj):
        count = EntryLog.objects.filter(labour=obj).count()
        inside = EntryLog.objects.filter(labour=obj, status='IN').exists()
        if inside:
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 2px 8px; '
                'border-radius: 3px;">{} (INSIDE)</span>', count
            )
        return count
    entry_count.short_description = "Entries"

    @admin.action(description="Activate selected labours")
    def activate_labours(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} labour(s) activated.")

    @admin.action(description="Deactivate selected labours")
    def deactivate_labours(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} labour(s) deactivated.")


@admin.register(EntryLog)
class EntryLogAdmin(admin.ModelAdmin):
    list_display = (
        "id", "photo_thumbnail", "name_snapshot", "person_type_badge", "status_badge",
        "gate_in_display", "gate_out_display", "entry_time_display", "duration_display", "created_by"
    )
    list_filter = (TodayEntryFilter, "status", "person_type", "gate_in", "gate_out", EntryDurationFilter, "entry_time")
    search_fields = ("name_snapshot", "visitor__name", "labour__name", "vehicle_no", "purpose")
    date_hierarchy = "entry_time"
    readonly_fields = (
        "entry_time", "created_at", "updated_at", "photo_preview",
        "duration_display_detail", "visitor_link", "labour_link"
    )
    autocomplete_fields = ("visitor", "labour", "gate_in", "gate_out", "person_type")
    list_per_page = 30
    ordering = ("-entry_time",)

    actions = ['mark_as_exited', 'mark_as_cancelled']

    fieldsets = (
        ("Person Information", {
            "fields": ("person_type", "name_snapshot", "photo_snapshot", "photo_preview"),
            "description": "Details about the person entering"
        }),
        ("Visitor/Labour Link", {
            "fields": ("visitor", "visitor_link", "labour", "labour_link"),
            "classes": ("collapse",)
        }),
        ("Movement Details", {
            "fields": ("gate_in", "gate_out", "entry_time", "exit_time", "status", "duration_display_detail")
        }),
        ("Business Information", {
            "fields": ("purpose", "approved_by", "vehicle_no", "remarks")
        }),
        ("Audit Trail", {
            "fields": ("created_by", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def photo_thumbnail(self, obj):
        if obj.photo_snapshot:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />',
                obj.photo_snapshot.url
            )
        # Try to get photo from visitor or labour
        photo_url = None
        if obj.visitor and obj.visitor.photo:
            photo_url = obj.visitor.photo.url
        elif obj.labour and obj.labour.photo:
            photo_url = obj.labour.photo.url

        if photo_url:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover; opacity: 0.7;" />',
                photo_url
            )
        return format_html(
            '<span style="display: inline-block; width: 40px; height: 40px; '
            'background-color: #e9ecef; border-radius: 50%; text-align: center; '
            'line-height: 40px; color: #6c757d;">{}</span>', "?"
        )
    photo_thumbnail.short_description = "Photo"

    def photo_preview(self, obj):
        if obj.photo_snapshot:
            return format_html(
                '<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 8px;" />',
                obj.photo_snapshot.url
            )
        return "No snapshot"
    photo_preview.short_description = "Photo Preview"

    def person_type_badge(self, obj):
        colors = {'Visitor': '#17a2b8', 'Labour': '#6f42c1'}
        color = colors.get(obj.person_type.name, '#6c757d') if obj.person_type else '#6c757d'
        name = obj.person_type.name if obj.person_type else 'Unknown'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, name.upper()
        )
    person_type_badge.short_description = "Type"

    def status_badge(self, obj):
        status_styles = {
            'IN': ('background-color: #28a745;', 'INSIDE'),
            'OUT': ('background-color: #6c757d;', 'EXITED'),
            'CANCELLED': ('background-color: #dc3545;', 'CANCELLED'),
        }
        style, text = status_styles.get(obj.status, ('background-color: #6c757d;', obj.status))
        return format_html(
            '<span style="{}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            style, text
        )
    status_badge.short_description = "Status"

    def gate_in_display(self, obj):
        return format_html(
            '<span style="color: #28a745;">IN</span> {}',
            obj.gate_in.name if obj.gate_in else '-'
        )
    gate_in_display.short_description = "Gate In"

    def gate_out_display(self, obj):
        if obj.gate_out:
            return format_html(
                '<span style="color: #dc3545;">OUT</span> {}',
                obj.gate_out.name
            )
        return "-"
    gate_out_display.short_description = "Gate Out"

    def entry_time_display(self, obj):
        return obj.entry_time.strftime("%d %b %Y %H:%M")
    entry_time_display.short_description = "Entry Time"
    entry_time_display.admin_order_field = "entry_time"

    def duration_display(self, obj):
        if obj.status == 'IN':
            duration = timezone.now() - obj.entry_time
        elif obj.exit_time:
            duration = obj.exit_time - obj.entry_time
        else:
            return "-"

        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes = remainder // 60

        if hours >= 8:
            color = '#dc3545'  # Red for long duration
        elif hours >= 4:
            color = '#ffc107'  # Yellow for medium
        else:
            color = '#28a745'  # Green for short

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}h {}m</span>',
            color, int(hours), int(minutes)
        )
    duration_display.short_description = "Duration"

    def duration_display_detail(self, obj):
        if obj.status == 'IN':
            duration = timezone.now() - obj.entry_time
            prefix = "Currently inside for"
        elif obj.exit_time:
            duration = obj.exit_time - obj.entry_time
            prefix = "Total duration"
        else:
            return "N/A"

        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes = remainder // 60
        return f"{prefix}: {int(hours)} hours {int(minutes)} minutes"
    duration_display_detail.short_description = "Duration Details"

    def visitor_link(self, obj):
        if obj.visitor:
            url = reverse('admin:person_gatein_visitor_change', args=[obj.visitor.id])
            return format_html('<a href="{}" target="_blank">View Visitor Details</a>', url)
        return "-"
    visitor_link.short_description = "Visitor Details"

    def labour_link(self, obj):
        if obj.labour:
            url = reverse('admin:person_gatein_labour_change', args=[obj.labour.id])
            return format_html('<a href="{}" target="_blank">View Labour Details</a>', url)
        return "-"
    labour_link.short_description = "Labour Details"

    @admin.action(description="Mark selected entries as EXITED")
    def mark_as_exited(self, request, queryset):
        updated = queryset.filter(status='IN').update(
            status='OUT',
            exit_time=timezone.now()
        )
        self.message_user(request, f"{updated} entry/entries marked as exited.")

    @admin.action(description="Mark selected entries as CANCELLED")
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.filter(status='IN').update(status='CANCELLED')
        self.message_user(request, f"{updated} entry/entries cancelled.")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'person_type', 'visitor', 'labour', 'gate_in', 'gate_out', 'created_by'
        )


# =========================================
# Admin Site Customization
# =========================================
admin.site.site_header = "Person Gate-In Management"
admin.site.site_title = "Gate-In Admin"
admin.site.index_title = "Welcome to Person Gate-In Management System"
