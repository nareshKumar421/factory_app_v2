from django.contrib import admin

from .models import DeviceToken, NotificationType, Notification, NotificationPreference


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "platform", "device_name", "is_active", "created_at", "last_used_at"]
    list_filter = ["platform", "is_active", "company"]
    search_fields = ["user__email", "device_name"]
    readonly_fields = ["created_at", "updated_at", "last_used_at"]
    raw_id_fields = ["user", "company"]


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["code", "name"]
    list_editable = ["is_active"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["recipient", "title", "status", "is_read", "company", "created_at"]
    list_filter = ["status", "is_read", "notification_type", "company"]
    search_fields = ["recipient__email", "title", "body"]
    readonly_fields = ["created_at", "sent_at", "read_at"]
    raw_id_fields = ["recipient", "company", "notification_type"]
    date_hierarchy = "created_at"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ["user", "notification_type", "is_enabled"]
    list_filter = ["notification_type", "is_enabled"]
    search_fields = ["user__email"]
    raw_id_fields = ["user"]
