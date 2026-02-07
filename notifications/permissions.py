from rest_framework.permissions import BasePermission


class CanSendNotification(BasePermission):
    """Permission to send manual notifications."""

    def has_permission(self, request, view):
        return request.user.has_perm("notifications.can_send_notification")


class CanSendBulkNotification(BasePermission):
    """Permission to send bulk/broadcast notifications."""

    def has_permission(self, request, view):
        return request.user.has_perm("notifications.can_send_bulk_notification")
