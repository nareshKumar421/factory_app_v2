from django.urls import path
from .views import (
    DeviceRegisterAPI,
    DeviceUnregisterAPI,
    NotificationListAPI,
    NotificationMarkReadAPI,
    NotificationUnreadCountAPI,
    SendNotificationAPI,
)

urlpatterns = [
    # Device token management
    path("devices/register/", DeviceRegisterAPI.as_view(), name="device-register"),
    path("devices/unregister/", DeviceUnregisterAPI.as_view(), name="device-unregister"),

    # Notification CRUD
    path("", NotificationListAPI.as_view(), name="notification-list"),
    path("mark-read/", NotificationMarkReadAPI.as_view(), name="notification-mark-read"),
    path("unread-count/", NotificationUnreadCountAPI.as_view(), name="notification-unread-count"),

    # Admin sending
    path("send/", SendNotificationAPI.as_view(), name="notification-send"),
]
