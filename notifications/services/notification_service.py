import logging
from typing import List, Optional

from django.db.models import Q
from django.utils import timezone

from accounts.models import User
from company.models import Company
from ..models import DeviceToken, Notification, NotificationType, NotificationPreference
from .fcm_service import FCMService

logger = logging.getLogger(__name__)


class NotificationService:
    """
    High-level notification service.
    Handles notification creation, recipient resolution, and delivery.
    """

    @staticmethod
    def register_device(
        user: User,
        token: str,
        platform: str,
        device_name: str = None,
        company: Company = None
    ) -> DeviceToken:
        """
        Register or update a device token for a user.
        """
        device_token, created = DeviceToken.objects.update_or_create(
            token=token,
            defaults={
                "user": user,
                "platform": platform.upper(),
                "device_name": device_name,
                "company": company,
                "is_active": True,
                "last_used_at": timezone.now(),
            }
        )

        action = "registered" if created else "updated"
        logger.info(f"Device token {action} for user {user.email}")

        return device_token

    @staticmethod
    def unregister_device(user: User, token: str) -> bool:
        """
        Unregister a device token (soft delete).
        """
        updated = DeviceToken.objects.filter(
            user=user,
            token=token
        ).update(is_active=False)

        return updated > 0

    @staticmethod
    def get_user_tokens(user: User, company: Company = None) -> List[str]:
        """
        Get all active device tokens for a user.
        """
        queryset = DeviceToken.objects.filter(
            user=user,
            is_active=True
        )

        if company:
            queryset = queryset.filter(
                Q(company=company) | Q(company__isnull=True)
            )

        return list(queryset.values_list("token", flat=True))

    @staticmethod
    def send_notification(
        notification_type_code: str,
        company: Company,
        recipients: List[User],
        context: dict = None,
        related_object: tuple = None,
    ) -> List[Notification]:
        """
        Send notification to specified recipients.

        Args:
            notification_type_code: Code from NotificationTypeCode enum
            company: Company context
            recipients: List of User objects
            context: Dict for template rendering
            related_object: Optional tuple (content_type, object_id)

        Returns:
            List of Notification objects created
        """
        try:
            notif_type = NotificationType.objects.get(
                code=notification_type_code,
                is_active=True
            )
        except NotificationType.DoesNotExist:
            logger.warning(f"Notification type not found: {notification_type_code}")
            return []

        context = context or {}

        # Render templates with context
        try:
            title = notif_type.title_template.format(**context)
            body = notif_type.body_template.format(**context)
        except KeyError as e:
            logger.error(f"Missing context key for notification template: {e}")
            return []

        notifications = []

        for recipient in recipients:
            # Check user preference
            pref = NotificationPreference.objects.filter(
                user=recipient,
                notification_type=notif_type
            ).first()

            if pref and not pref.is_enabled:
                logger.debug(f"Notification disabled for user {recipient.email}")
                continue

            # Create notification record
            notification = Notification.objects.create(
                notification_type=notif_type,
                company=company,
                recipient=recipient,
                title=title,
                body=body,
                data=context,
                content_type=related_object[0] if related_object else None,
                object_id=related_object[1] if related_object else None,
                status="PENDING"
            )

            # Get device tokens
            tokens = NotificationService.get_user_tokens(recipient, company)

            if not tokens:
                notification.status = "FAILED"
                notification.error_message = "No active device tokens"
                notification.save()
                notifications.append(notification)
                continue

            # Send via FCM
            result = FCMService.send_to_multiple(
                tokens=tokens,
                title=title,
                body=body,
                data={
                    "notification_id": str(notification.id),
                    "type": notification_type_code,
                    **{k: str(v) for k, v in context.items()}
                }
            )

            # Update notification status
            if result.get("success_count", 0) > 0:
                notification.status = "SENT"
                notification.sent_at = timezone.now()
            else:
                notification.status = "FAILED"
                notification.error_message = result.get("error", "All tokens failed")

            notification.save()
            notifications.append(notification)

            # Deactivate unregistered tokens
            for resp in result.get("responses", []):
                if not resp.get("success") and "TOKEN_UNREGISTERED" in str(resp.get("error", "")):
                    DeviceToken.objects.filter(token=resp["token"]).update(is_active=False)

        return notifications

    @staticmethod
    def notify_user(
        notification_type_code: str,
        company: Company,
        user: User,
        context: dict = None,
        related_object: tuple = None,
    ) -> Optional[Notification]:
        """
        Send notification to a specific user.
        """
        notifications = NotificationService.send_notification(
            notification_type_code=notification_type_code,
            company=company,
            recipients=[user],
            context=context,
            related_object=related_object,
        )
        return notifications[0] if notifications else None
