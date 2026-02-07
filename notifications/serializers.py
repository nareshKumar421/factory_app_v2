from rest_framework import serializers
from .models import Notification


class DeviceRegistrationSerializer(serializers.Serializer):
    fcm_token = serializers.CharField(required=True)
    device_type = serializers.ChoiceField(
        choices=["WEB", "ANDROID", "IOS"],
        default="WEB"
    )
    device_info = serializers.CharField(required=False, allow_blank=True, default="")


class DeviceUnregisterSerializer(serializers.Serializer):
    fcm_token = serializers.CharField(required=True)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "body",
            "notification_type",
            "click_action_url",
            "reference_type",
            "reference_id",
            "is_read",
            "read_at",
            "extra_data",
            "created_at",
        ]


class NotificationMarkReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[],
        help_text="List of notification IDs to mark as read. If empty, marks all as read."
    )


class SendNotificationSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    body = serializers.CharField()
    notification_type = serializers.CharField(default="GENERAL_ANNOUNCEMENT")
    click_action_url = serializers.CharField(required=False, allow_blank=True, default="")
    recipient_user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[],
        help_text="Specific user IDs. If empty, sends to all company users."
    )
    role_filter = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Filter recipients by role name"
    )
