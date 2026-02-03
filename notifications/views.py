from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from company.permissions import HasCompanyContext
from .models import DeviceToken, Notification, NotificationType, NotificationPreference
from .serializers import (
    DeviceTokenSerializer,
    DeviceTokenRegisterSerializer,
    DeviceTokenUnregisterSerializer,
    NotificationSerializer,
    NotificationListSerializer,
    NotificationPreferenceSerializer,
    MarkNotificationReadSerializer,
)
from .services import NotificationService
from .services.fcm_service import FCMService


class DeviceTokenView(APIView):
    """
    Manage device tokens for push notifications.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List user's registered device tokens."""
        tokens = DeviceToken.objects.filter(
            user=request.user,
            is_active=True
        )
        serializer = DeviceTokenSerializer(tokens, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Register a new device token."""
        serializer = DeviceTokenRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get company from header if available
        company = None
        if hasattr(request, 'company'):
            company = request.company.company

        device_token = NotificationService.register_device(
            user=request.user,
            token=serializer.validated_data["token"],
            platform=serializer.validated_data["platform"],
            device_name=serializer.validated_data.get("device_name"),
            company=company,
        )

        return Response(
            DeviceTokenSerializer(device_token).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request):
        """Unregister a device token."""
        serializer = DeviceTokenUnregisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        success = NotificationService.unregister_device(
            user=request.user,
            token=serializer.validated_data["token"]
        )

        if success:
            return Response({"message": "Device token unregistered"})
        return Response(
            {"error": "Device token not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasCompanyContext])
def notification_list(request):
    """
    List notifications for the current user in company context.

    Query Parameters:
    - is_read: Filter by read status (true/false)
    - limit: Number of notifications to return (default: 50)
    - offset: Pagination offset
    """
    company = request.company.company

    notifications = Notification.objects.filter(
        recipient=request.user,
        company=company
    )

    # Filter by read status
    is_read = request.query_params.get("is_read")
    if is_read is not None:
        is_read_bool = is_read.lower() == "true"
        notifications = notifications.filter(is_read=is_read_bool)

    # Pagination
    limit = int(request.query_params.get("limit", 50))
    offset = int(request.query_params.get("offset", 0))

    total_count = notifications.count()
    unread_count = notifications.filter(is_read=False).count()

    notifications = notifications[offset:offset + limit]
    serializer = NotificationListSerializer(notifications, many=True)

    return Response({
        "count": total_count,
        "unread_count": unread_count,
        "results": serializer.data
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasCompanyContext])
def notification_detail(request, pk):
    """Get notification detail and mark as read."""
    try:
        notification = Notification.objects.get(
            pk=pk,
            recipient=request.user,
            company=request.company.company
        )
    except Notification.DoesNotExist:
        return Response(
            {"error": "Notification not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Mark as read
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=["is_read", "read_at"])

    serializer = NotificationSerializer(notification)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasCompanyContext])
def mark_notifications_read(request):
    """Mark notifications as read."""
    serializer = MarkNotificationReadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    company = request.company.company
    notification_ids = serializer.validated_data.get("notification_ids")

    queryset = Notification.objects.filter(
        recipient=request.user,
        company=company,
        is_read=False
    )

    if notification_ids:
        queryset = queryset.filter(id__in=notification_ids)

    updated_count = queryset.update(
        is_read=True,
        read_at=timezone.now()
    )

    return Response({
        "message": f"{updated_count} notification(s) marked as read"
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def unread_count(request):
    """Get unread notification count across all companies."""
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()

    return Response({"unread_count": count})


class NotificationPreferenceView(APIView):
    """Manage notification preferences."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all notification types with user preferences."""
        notification_types = NotificationType.objects.filter(is_active=True)

        preferences = {
            p.notification_type_id: p.is_enabled
            for p in NotificationPreference.objects.filter(user=request.user)
        }

        result = []
        for nt in notification_types:
            result.append({
                "id": nt.id,
                "code": nt.code,
                "name": nt.name,
                "description": nt.description,
                "is_enabled": preferences.get(nt.id, True)  # Default enabled
            })

        return Response(result)

    def post(self, request):
        """Update notification preference."""
        serializer = NotificationPreferenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pref, created = NotificationPreference.objects.update_or_create(
            user=request.user,
            notification_type_id=serializer.validated_data["notification_type_id"],
            defaults={"is_enabled": serializer.validated_data["is_enabled"]}
        )

        return Response(NotificationPreferenceSerializer(pref).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def test_fcm_notification(request):
    """
    Test endpoint to send FCM push notification.

    Request body:
    {
        "token": "device_fcm_token",
        "title": "Test Title",
        "body": "Test message body"
    }
    """
    token = request.data.get("token")
    title = request.data.get("title", "Test Notification")
    body = request.data.get("body", "This is a test notification")

    if not token:
        return Response(
            {"error": "token is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    result = FCMService.send_to_token(
        token=token,
        title=title,
        body=body
    )

    if result["success"]:
        return Response(result)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
