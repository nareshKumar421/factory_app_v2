import logging
from datetime import timedelta
from typing import List, Dict, Any

from django.conf import settings
from django.utils import timezone
from django.db import transaction

import firebase_admin
from firebase_admin import credentials, messaging

from .models import UserDevice, Notification, NotificationType

logger = logging.getLogger(__name__)

# Firebase Admin SDK singleton
_firebase_app = None


def get_firebase_app():
    global _firebase_app
    if _firebase_app is None:
        cred = credentials.Certificate(settings.FCM_CREDENTIALS_PATH)
        _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app


class NotificationService:

    @staticmethod
    def register_device(user, fcm_token: str, device_type: str = "WEB",
                        device_info: str = "") -> UserDevice:
        """
        Register or update an FCM device token for a user.
        If the token exists for another user, reassign it.
        """
        UserDevice.objects.filter(fcm_token=fcm_token).exclude(user=user).delete()

        device, _ = UserDevice.objects.update_or_create(
            fcm_token=fcm_token,
            defaults={
                "user": user,
                "device_type": device_type,
                "device_info": device_info,
                "is_active": True,
            }
        )
        return device

    @staticmethod
    def unregister_device(user, fcm_token: str) -> bool:
        """Unregister a specific FCM token for a user."""
        deleted_count, _ = UserDevice.objects.filter(
            user=user,
            fcm_token=fcm_token
        ).delete()
        return deleted_count > 0

    @staticmethod
    def cleanup_stale_tokens(days: int = 30) -> int:
        """Remove device tokens not used in the specified number of days."""
        cutoff = timezone.now() - timedelta(days=days)
        stale = UserDevice.objects.filter(last_used_at__lt=cutoff)
        count = stale.count()
        stale.delete()
        logger.info(f"Cleaned up {count} stale FCM tokens")
        return count

    @staticmethod
    def _build_fcm_message(token: str, title: str, body: str,
                           data: Dict[str, str] = None,
                           click_action_url: str = "") -> messaging.Message:
        fcm_data = data or {}
        if click_action_url:
            fcm_data["click_action_url"] = click_action_url

        webpush_kwargs = {
            "notification": messaging.WebpushNotification(
                title=title,
                body=body,
                icon="/icons/notification-icon.png",
            ),
        }

        if click_action_url and click_action_url.startswith("https://"):
            webpush_kwargs["fcm_options"] = messaging.WebpushFCMOptions(
                link=click_action_url,
            )

        return messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=fcm_data,
            token=token,
            webpush=messaging.WebpushConfig(**webpush_kwargs),
        )

    @classmethod
    def _send_to_tokens(cls, tokens: List[str], title: str, body: str,
                        data: Dict[str, str] = None,
                        click_action_url: str = "") -> Dict[str, Any]:
        """
        Send push notification to multiple FCM tokens.
        Returns dict with success/failure counts and failed tokens.
        """
        if not tokens:
            return {"success_count": 0, "failure_count": 0, "failed_tokens": []}

        app = get_firebase_app()
        failed_tokens = []
        success_count = 0

        for token in tokens:
            try:
                message = cls._build_fcm_message(
                    token=token, title=title, body=body,
                    data=data, click_action_url=click_action_url
                )
                messaging.send(message, app=app)
                success_count += 1
            except messaging.UnregisteredError:
                failed_tokens.append(token)
                UserDevice.objects.filter(fcm_token=token).update(is_active=False)
            except Exception as e:
                logger.error(f"FCM send error for token {token[:20]}...: {e}")
                failed_tokens.append(token)

        return {
            "success_count": success_count,
            "failure_count": len(failed_tokens),
            "failed_tokens": failed_tokens,
        }

    @classmethod
    @transaction.atomic
    def send_notification_to_user(
        cls,
        user,
        title: str,
        body: str,
        notification_type: str = NotificationType.GENERAL_ANNOUNCEMENT,
        click_action_url: str = "",
        reference_type: str = "",
        reference_id: int = None,
        company=None,
        extra_data: dict = None,
        created_by=None, 
    ) -> Notification:
        """
        Send notification to a specific user on all their devices.
        Creates a stored Notification record and sends FCM push.
        """
        notification = Notification.objects.create(
            recipient=user,
            company=company,
            title=title,
            body=body,
            notification_type=notification_type,
            click_action_url=click_action_url,
            reference_type=reference_type,
            reference_id=reference_id,
            extra_data=extra_data or {},
            created_by=created_by,
        )

        tokens = list(
            UserDevice.objects.filter(
                user=user, is_active=True
            ).values_list("fcm_token", flat=True)
        )

        if tokens:
            fcm_data = {
                "notification_id": str(notification.id),
                "notification_type": notification_type,
                "reference_type": reference_type,
                "reference_id": str(reference_id or ""),
            }

            result = cls._send_to_tokens(
                tokens=tokens,
                title=title,
                body=body,
                data=fcm_data,
                click_action_url=click_action_url,
            )
            logger.info(
                f"Notification sent to {user.email}: "
                f"{result['success_count']} success, "
                f"{result['failure_count']} failed"
            )

        return notification

    @classmethod
    def send_notification_to_group(
        cls,
        users,
        title: str,
        body: str,
        notification_type: str = NotificationType.GENERAL_ANNOUNCEMENT,
        click_action_url: str = "",
        reference_type: str = "",
        reference_id: int = None,
        company=None,
        extra_data: dict = None,
        created_by=None,
    ) -> List[Notification]:
        """Send notification to a list of users."""
        notifications = []
        for user in users:
            notification = cls.send_notification_to_user(
                user=user,
                title=title,
                body=body,
                notification_type=notification_type,
                click_action_url=click_action_url,
                reference_type=reference_type,
                reference_id=reference_id,
                company=company,
                extra_data=extra_data,
                created_by=created_by,
            )
            notifications.append(notification)
        return notifications

    @classmethod
    def send_bulk_notification(
        cls,
        company,
        title: str,
        body: str,
        notification_type: str = NotificationType.GENERAL_ANNOUNCEMENT,
        click_action_url: str = "",
        role_name: str = None,
        created_by=None,
    ) -> int:
        """
        Send notification to all users in a company.
        Optionally filter by role name.
        """
        from company.models import UserCompany

        queryset = UserCompany.objects.filter(
            company=company, is_active=True
        ).select_related("user")

        if role_name:
            queryset = queryset.filter(role__name=role_name)

        users = [uc.user for uc in queryset]
        notifications = cls.send_notification_to_group(
            users=users,
            title=title,
            body=body,
            notification_type=notification_type,
            click_action_url=click_action_url,
            company=company,
            created_by=created_by,
        )
        return len(notifications)

    @classmethod
    def send_notification_by_permission(
        cls,
        permission_codename: str,
        title: str,
        body: str,
        notification_type: str = NotificationType.GENERAL_ANNOUNCEMENT,
        click_action_url: str = "",
        company=None,
        extra_data: dict = None,
        created_by=None,
    ) -> int:
        """
        Send notification to all active users who have a specific permission.
        Permission can be assigned directly or via a group.
        """
        from django.contrib.auth import get_user_model
        from django.db.models import Q

        User = get_user_model()

        users = User.objects.filter(
            Q(user_permissions__codename=permission_codename) |
            Q(groups__permissions__codename=permission_codename),
            is_active=True,
        ).distinct()

        if company:
            from company.models import UserCompany
            company_user_ids = UserCompany.objects.filter(
                company=company, is_active=True
            ).values_list("user_id", flat=True)
            users = users.filter(id__in=company_user_ids)

        notifications = cls.send_notification_to_group(
            users=users,
            title=title,
            body=body,
            notification_type=notification_type,
            click_action_url=click_action_url,
            company=company,
            extra_data=extra_data,
            created_by=created_by,
        )
        return len(notifications)

    @classmethod
    def send_notification_by_auth_group(
        cls,
        group_name: str,
        title: str,
        body: str,
        notification_type: str = NotificationType.GENERAL_ANNOUNCEMENT,
        click_action_url: str = "",
        company=None,
        extra_data: dict = None,
        created_by=None,
    ) -> int:
        """
        Send notification to all active users in a Django auth group.
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()

        users = User.objects.filter(
            groups__name=group_name,
            is_active=True,
        ).distinct()

        if company:
            from company.models import UserCompany
            company_user_ids = UserCompany.objects.filter(
                company=company, is_active=True
            ).values_list("user_id", flat=True)
            users = users.filter(id__in=company_user_ids)

        notifications = cls.send_notification_to_group(
            users=users,
            title=title,
            body=body,
            notification_type=notification_type,
            click_action_url=click_action_url,
            company=company,
            extra_data=extra_data,
            created_by=created_by,
        )
        return len(notifications)
