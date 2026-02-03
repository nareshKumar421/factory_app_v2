from django.urls import path

from .views import (
    DeviceTokenView,
    NotificationPreferenceView,
    notification_list,
    notification_detail,
    mark_notifications_read,
    unread_count,
    test_fcm_notification,
)

urlpatterns = [
    # Device Token Management
    path("device-tokens/", DeviceTokenView.as_view(), name="device-tokens"),

    # Notifications
    path("", notification_list, name="notification-list"),
    path("<int:pk>/", notification_detail, name="notification-detail"),
    path("mark-read/", mark_notifications_read, name="mark-notifications-read"),
    path("unread-count/", unread_count, name="unread-count"),

    # Preferences
    path("preferences/", NotificationPreferenceView.as_view(), name="notification-preferences"),

    # Test endpoint
    path("test/", test_fcm_notification, name="test-fcm-notification"),
]
