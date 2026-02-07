from django.contrib import admin
from .models import UserDevice, Notification


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ["user", "device_type", "is_active", "created_at", "last_used_at"]
    list_filter = ["device_type", "is_active"]
    search_fields = ["user__email", "user__full_name"]
    readonly_fields = ["fcm_token", "created_at", "last_used_at"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "id", "title", "recipient", "notification_type",
        "is_read", "created_at"
    ]
    list_filter = ["notification_type", "is_read", "created_at"]
    search_fields = ["title", "body", "recipient__email"]
    readonly_fields = [
        "recipient", "company", "title", "body",
        "notification_type", "click_action_url",
        "reference_type", "reference_id",
        "is_read", "read_at", "extra_data",
        "created_at", "created_by",
    ]
