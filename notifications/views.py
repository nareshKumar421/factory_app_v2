import logging

from django.db import models
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from company.permissions import HasCompanyContext
from .models import Notification
from .services import NotificationService
from .serializers import (
    DeviceRegistrationSerializer,
    DeviceUnregisterSerializer,
    NotificationSerializer,
    NotificationMarkReadSerializer,
    SendNotificationSerializer,
)
from .permissions import CanSendNotification

logger = logging.getLogger(__name__)


class DeviceRegisterAPI(APIView):
    """
    Register FCM device token for the authenticated user.
    POST /api/v1/notifications/devices/register/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeviceRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        device = NotificationService.register_device(
            user=request.user,
            fcm_token=serializer.validated_data["fcm_token"],
            device_type=serializer.validated_data.get("device_type", "WEB"),
            device_info=serializer.validated_data.get("device_info", ""),
        )

        return Response(
            {"message": "Device registered successfully", "device_id": device.id},
            status=status.HTTP_201_CREATED
        )


class DeviceUnregisterAPI(APIView):
    """
    Unregister FCM device token (on logout).
    POST /api/v1/notifications/devices/unregister/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeviceUnregisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        removed = NotificationService.unregister_device(
            user=request.user,
            fcm_token=serializer.validated_data["fcm_token"],
        )

        if removed:
            return Response({"message": "Device unregistered successfully"})
        return Response(
            {"detail": "Device token not found"},
            status=status.HTTP_404_NOT_FOUND
        )


class NotificationListAPI(APIView):
    """
    List notifications for the authenticated user.
    GET /api/v1/notifications/
    Query params: ?is_read=true|false&type=GRPO_POSTED&page=1&page_size=20
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Notification.objects.filter(recipient=request.user)

        # Filter by company if header present
        company_code = request.headers.get("Company-Code")
        if company_code:
            queryset = queryset.filter(
                models.Q(company__code=company_code) | models.Q(company__isnull=True)
            )

        # Filter by read status
        is_read = request.query_params.get("is_read")
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == "true")

        # Filter by type
        ntype = request.query_params.get("type")
        if ntype:
            queryset = queryset.filter(notification_type=ntype)

        # Simple pagination
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
        page_size = min(page_size, 100)

        start = (page - 1) * page_size
        end = start + page_size

        total_count = queryset.count()
        unread_count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        notifications = queryset[start:end]

        serializer = NotificationSerializer(notifications, many=True)

        return Response({
            "results": serializer.data,
            "total_count": total_count,
            "unread_count": unread_count,
            "page": page,
            "page_size": page_size,
        })


class NotificationMarkReadAPI(APIView):
    """
    Mark notifications as read.
    POST /api/v1/notifications/mark-read/
    Body: {"notification_ids": [1, 2, 3]} or {} to mark all as read.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NotificationMarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        notification_ids = serializer.validated_data.get("notification_ids", [])
        now = timezone.now()

        queryset = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        )

        if notification_ids:
            queryset = queryset.filter(id__in=notification_ids)

        updated = queryset.update(is_read=True, read_at=now)

        return Response({"marked_read": updated})


class NotificationUnreadCountAPI(APIView):
    """
    Get unread notification count.
    GET /api/v1/notifications/unread-count/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count()
        return Response({"unread_count": count})


class SendNotificationAPI(APIView):
    """
    Admin endpoint to send manual notifications.
    POST /api/v1/notifications/send/
    Requires: notifications.can_send_notification permission.
    """
    permission_classes = [IsAuthenticated, HasCompanyContext, CanSendNotification]

    def post(self, request):
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        company = request.company.company
        recipient_user_ids = data.get("recipient_user_ids", [])
        role_filter = data.get("role_filter", "")

        if recipient_user_ids:
            from accounts.models import User
            users = User.objects.filter(id__in=recipient_user_ids, is_active=True)
            notifications = NotificationService.send_notification_to_group(
                users=users,
                title=data["title"],
                body=data["body"],
                notification_type=data.get("notification_type", "GENERAL_ANNOUNCEMENT"),
                click_action_url=data.get("click_action_url", ""),
                company=company,
                created_by=request.user,
            )
            count = len(notifications)
        else:
            count = NotificationService.send_bulk_notification(
                company=company,
                title=data["title"],
                body=data["body"],
                notification_type=data.get("notification_type", "GENERAL_ANNOUNCEMENT"),
                click_action_url=data.get("click_action_url", ""),
                role_name=role_filter or None,
                created_by=request.user,
            )

        return Response({
            "message": f"Notification sent to {count} users",
            "recipients_count": count,
        })
