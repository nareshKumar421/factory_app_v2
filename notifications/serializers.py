from rest_framework import serializers

from .models import DeviceToken, Notification, NotificationType, NotificationPreference


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = [
            "id", "token", "platform", "device_name",
            "is_active", "created_at", "last_used_at"
        ]
        read_only_fields = ["id", "is_active", "created_at", "last_used_at"]


class DeviceTokenRegisterSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=500)
    platform = serializers.ChoiceField(choices=["ANDROID", "IOS", "WEB"])
    device_name = serializers.CharField(max_length=100, required=False, allow_blank=True)


class DeviceTokenUnregisterSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=500)


class NotificationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationType
        fields = ["id", "code", "name", "description", "is_active"]


class NotificationSerializer(serializers.ModelSerializer):
    notification_type = NotificationTypeSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id", "notification_type", "title", "body", "data",
            "content_type", "object_id", "status", "is_read",
            "read_at", "created_at", "sent_at"
        ]
        read_only_fields = fields


class NotificationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    type_code = serializers.CharField(source="notification_type.code", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id", "type_code", "title", "body", "is_read", "created_at"
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    notification_type = NotificationTypeSerializer(read_only=True)
    notification_type_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = NotificationPreference
        fields = ["id", "notification_type", "notification_type_id", "is_enabled"]
        read_only_fields = ["id"]


class MarkNotificationReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of notification IDs to mark as read. If empty, marks all as read."
    )
