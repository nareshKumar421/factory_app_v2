from django.db import models
from django.conf import settings

from company.models import Company


class DeviceToken(models.Model):
    """
    Stores FCM device tokens for push notification delivery.
    Supports multiple devices per user and company-scoped tokens.
    """
    PLATFORM_CHOICES = (
        ("ANDROID", "Android"),
        ("IOS", "iOS"),
        ("WEB", "Web"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="device_tokens"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="device_tokens",
        null=True,
        blank=True,
        help_text="If set, token is scoped to this company context"
    )
    token = models.TextField(unique=True)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES, default="ANDROID")
    device_name = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["company", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.platform} - {self.device_name or 'Unknown'}"


class NotificationType(models.Model):
    """
    Master table for notification types with configurable settings.
    """
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    title_template = models.CharField(max_length=200)
    body_template = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Notification(models.Model):
    """
    Logs all sent notifications for audit and history.
    """
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("SENT", "Sent"),
        ("FAILED", "Failed"),
        ("DELIVERED", "Delivered"),
    )

    notification_type = models.ForeignKey(
        NotificationType,
        on_delete=models.SET_NULL,
        null=True,
        related_name="notifications"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_notifications"
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    content_type = models.CharField(max_length=50, blank=True, null=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    fcm_message_id = models.CharField(max_length=200, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["company", "created_at"]),
            models.Index(fields=["status"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient.email} - {self.title[:50]}"


class NotificationPreference(models.Model):
    """
    User preferences for notification types.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences"
    )
    notification_type = models.ForeignKey(
        NotificationType,
        on_delete=models.CASCADE,
        related_name="user_preferences"
    )
    is_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = [("user", "notification_type")]

    def __str__(self):
        status = "Enabled" if self.is_enabled else "Disabled"
        return f"{self.user.email} - {self.notification_type.code} - {status}"
