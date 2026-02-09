# Notifications Commands Reference

All management commands, Django shell utilities, and useful queries for the notifications app.

---

## Management Commands

### `cleanup_stale_fcm_tokens`

Remove FCM device tokens that have not been used for a specified number of days. Stale tokens accumulate when users uninstall the app or stop using a browser without explicitly logging out.

```bash
# Default: remove tokens not used in 30 days
python manage.py cleanup_stale_fcm_tokens

# Custom threshold: remove tokens not used in 7 days
python manage.py cleanup_stale_fcm_tokens --days 7

# Remove tokens not used in 60 days
python manage.py cleanup_stale_fcm_tokens --days 60
```

**Arguments:**

| Flag     | Type | Default | Description                              |
|----------|------|---------|------------------------------------------|
| `--days` | int  | `30`    | Remove tokens not used in this many days |

**Output:**

```
Cleaned up 12 stale FCM tokens (older than 30 days)
```

**Scheduling with cron (Linux):**

```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/factory_app && python manage.py cleanup_stale_fcm_tokens --days 30
```

**Scheduling with Windows Task Scheduler:**

```
Program: python
Arguments: manage.py cleanup_stale_fcm_tokens --days 30
Start in: D:\factory_app
Trigger: Daily at 2:00 AM
```

---

## Django Shell Commands

Open the Django shell with:

```bash
python manage.py shell
```

### Import Essentials

```python
from accounts.models import User
from company.models import Company, UserCompany
from notifications.models import UserDevice, Notification, NotificationType
from notifications.services import NotificationService
```

---

### Device Management

#### List all registered devices

```python
UserDevice.objects.all().values("id", "user__email", "device_type", "is_active", "last_used_at")
```

#### List devices for a specific user

```python
UserDevice.objects.filter(user__email="user@example.com").values(
    "id", "fcm_token", "device_type", "device_info", "is_active", "last_used_at"
)
```

#### Count active devices per user

```python
from django.db.models import Count
UserDevice.objects.filter(is_active=True).values("user__email").annotate(
    device_count=Count("id")
).order_by("-device_count")
```

#### Deactivate all devices for a user

```python
UserDevice.objects.filter(user__email="user@example.com").update(is_active=False)
```

#### Delete inactive devices

```python
count, _ = UserDevice.objects.filter(is_active=False).delete()
print(f"Deleted {count} inactive devices")
```

#### Register a device via service

```python
user = User.objects.get(email="user@example.com")
device = NotificationService.register_device(
    user=user,
    fcm_token="your-fcm-token-here",
    device_type="WEB",
    device_info="Chrome 120 / Windows"
)
print(f"Device registered: id={device.id}")
```

#### Manually clean up stale tokens

```python
count = NotificationService.cleanup_stale_tokens(days=30)
print(f"Removed {count} stale tokens")
```

---

### Send Notifications

#### Send to a single user

```python
user = User.objects.get(email="user@example.com")
company = Company.objects.get(code="JIVO_OIL")

notification = NotificationService.send_notification_to_user(
    user=user,
    title="Test Notification",
    body="This is a test notification from Django shell.",
    notification_type=NotificationType.GENERAL_ANNOUNCEMENT,
    click_action_url="/dashboard",
    company=company,
)
print(f"Sent: id={notification.id}")
```

#### Send to multiple users

```python
users = User.objects.filter(email__in=["user1@example.com", "user2@example.com"])

notifications = NotificationService.send_notification_to_group(
    users=users,
    title="Team Update",
    body="All members please review the latest changes.",
    notification_type=NotificationType.GENERAL_ANNOUNCEMENT,
    click_action_url="/updates",
)
print(f"Sent to {len(notifications)} users")
```

#### Broadcast to all users in a company

```python
company = Company.objects.get(code="JIVO_OIL")

count = NotificationService.send_bulk_notification(
    company=company,
    title="System Maintenance",
    body="Scheduled maintenance at 11 PM IST tonight.",
    notification_type=NotificationType.GENERAL_ANNOUNCEMENT,
    click_action_url="/announcements",
)
print(f"Sent to {count} users")
```

#### Broadcast to users with a specific role

```python
company = Company.objects.get(code="JIVO_OIL")

count = NotificationService.send_bulk_notification(
    company=company,
    title="QC Report Pending",
    body="Please complete pending inspections by EOD.",
    notification_type=NotificationType.GENERAL_ANNOUNCEMENT,
    click_action_url="/quality-control",
    role_name="QC",
)
print(f"Sent to {count} QC users")
```

#### Send to all users with a specific permission

```python
company = Company.objects.get(code="JIVO_OIL")

count = NotificationService.send_notification_by_permission(
    permission_codename="view_grpoposting",
    title="GRPO Batch Complete",
    body="All pending GRPO postings have been processed.",
    notification_type=NotificationType.GENERAL_ANNOUNCEMENT,
    click_action_url="/grpo",
    company=company,
)
print(f"Sent to {count} users with view_grpoposting permission")
```

#### Send to all users with a permission (without company scope)

```python
# Sends to ALL users across all companies who have this permission
count = NotificationService.send_notification_by_permission(
    permission_codename="can_send_notification",
    title="Admin Notice",
    body="New notification features have been deployed.",
)
print(f"Sent to {count} users")
```

#### Send to all users in a Django auth group

```python
company = Company.objects.get(code="JIVO_OIL")

count = NotificationService.send_notification_by_auth_group(
    group_name="quality_control",
    title="QC Report Due",
    body="All pending inspections must be completed by EOD.",
    notification_type=NotificationType.GENERAL_ANNOUNCEMENT,
    click_action_url="/quality-control",
    company=company,
)
print(f"Sent to {count} quality_control group users")
```

#### Send to a group (without company scope)

```python
count = NotificationService.send_notification_by_auth_group(
    group_name="grpo",
    title="SAP Sync Complete",
    body="All GRPO postings synced with SAP successfully.",
    click_action_url="/grpo",
)
print(f"Sent to {count} grpo group users")
```

#### List available groups and permissions

```python
from django.contrib.auth.models import Group, Permission

# List all groups
for g in Group.objects.all():
    print(f"  {g.name} ({g.user_set.count()} users)")

# List permissions for an app
Permission.objects.filter(
    content_type__app_label="grpo"
).values_list("codename", flat=True)
```

---

### Query Notifications

#### List recent notifications for a user

```python
Notification.objects.filter(
    recipient__email="user@example.com"
).values("id", "title", "notification_type", "is_read", "created_at")[:10]
```

#### Count unread notifications

```python
count = Notification.objects.filter(
    recipient__email="user@example.com",
    is_read=False
).count()
print(f"Unread: {count}")
```

#### Filter by notification type

```python
Notification.objects.filter(
    notification_type=NotificationType.GRPO_POSTED
).values("id", "title", "recipient__email", "created_at")[:10]
```

#### Filter by company

```python
Notification.objects.filter(
    company__code="JIVO_OIL"
).values("id", "title", "notification_type", "recipient__email")[:10]
```

#### Get notifications for a specific entity

```python
# All notifications referencing a specific VehicleEntry
Notification.objects.filter(
    reference_type="vehicle_entry",
    reference_id=42
).values("id", "title", "notification_type", "recipient__email", "is_read")
```

---

### Mark Read / Unread

#### Mark specific notifications as read

```python
from django.utils import timezone

Notification.objects.filter(id__in=[1, 2, 3]).update(
    is_read=True,
    read_at=timezone.now()
)
```

#### Mark all unread notifications as read for a user

```python
from django.utils import timezone

count = Notification.objects.filter(
    recipient__email="user@example.com",
    is_read=False
).update(is_read=True, read_at=timezone.now())
print(f"Marked {count} as read")
```

#### Reset a notification to unread

```python
Notification.objects.filter(id=42).update(is_read=False, read_at=None)
```

---

### Bulk Operations

#### Delete old notifications (older than 90 days)

```python
from django.utils import timezone
from datetime import timedelta

cutoff = timezone.now() - timedelta(days=90)
count, _ = Notification.objects.filter(created_at__lt=cutoff).delete()
print(f"Deleted {count} old notifications")
```

#### Delete all notifications for a company

```python
count, _ = Notification.objects.filter(company__code="JIVO_OIL").delete()
print(f"Deleted {count} notifications")
```

#### Count notifications by type

```python
from django.db.models import Count

Notification.objects.values("notification_type").annotate(
    total=Count("id")
).order_by("-total")
```

#### Count notifications per user

```python
from django.db.models import Count

Notification.objects.values("recipient__email").annotate(
    total=Count("id"),
    unread=Count("id", filter=models.Q(is_read=False))
).order_by("-total")[:20]
```

---

### Statistics & Debugging

#### Total notification stats

```python
total = Notification.objects.count()
unread = Notification.objects.filter(is_read=False).count()
devices = UserDevice.objects.filter(is_active=True).count()

print(f"Total notifications: {total}")
print(f"Unread: {unread}")
print(f"Active devices: {devices}")
```

#### Notifications sent today

```python
from django.utils import timezone

today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
count = Notification.objects.filter(created_at__gte=today_start).count()
print(f"Sent today: {count}")
```

#### Check if signals are connected

```python
from django.db.models.signals import post_save

for entry in post_save.receivers:
    receiver = entry[1]()
    if receiver and hasattr(receiver, '__name__') and 'notify_' in receiver.__name__:
        sender = entry[2]()
        sender_name = sender.__name__ if sender else 'Any'
        print(f"  {receiver.__name__} -> {sender_name}")
```

#### Check Firebase connection

```python
from notifications.services import get_firebase_app

try:
    app = get_firebase_app()
    print(f"Firebase app initialized: {app.name}")
    print(f"Project ID: {app.project_id}")
except Exception as e:
    print(f"Firebase error: {e}")
```

---

## Cron / Scheduled Tasks

Recommended scheduled tasks for production:

| Task | Command | Schedule | Purpose |
|------|---------|----------|---------|
| Cleanup stale tokens | `python manage.py cleanup_stale_fcm_tokens --days 30` | Daily at 2 AM | Remove unused FCM tokens |
| Delete old notifications | Custom script (see Bulk Operations) | Weekly | Keep database lean |

### Example: Cron Setup (Linux)

```bash
# Edit crontab
crontab -e

# Add these lines:
# Cleanup stale FCM tokens daily at 2 AM
0 2 * * * cd /path/to/factory_app && /path/to/venv/bin/python manage.py cleanup_stale_fcm_tokens --days 30 >> /var/log/fcm_cleanup.log 2>&1
```

### Example: Celery Beat (if using Celery)

```python
# config/celery.py or config/settings.py
CELERY_BEAT_SCHEDULE = {
    'cleanup-stale-fcm-tokens': {
        'task': 'notifications.tasks.cleanup_stale_tokens',
        'schedule': crontab(hour=2, minute=0),
    },
}
```

```python
# notifications/tasks.py
from celery import shared_task
from notifications.services import NotificationService

@shared_task
def cleanup_stale_tokens():
    count = NotificationService.cleanup_stale_tokens(days=30)
    return f"Cleaned up {count} stale tokens"
```

---

## Quick Reference

```bash
# Management commands
python manage.py cleanup_stale_fcm_tokens           # Default 30 days
python manage.py cleanup_stale_fcm_tokens --days 7   # Custom days

# Django shell one-liners
python manage.py shell -c "from notifications.models import *; print(Notification.objects.count())"
python manage.py shell -c "from notifications.models import *; print(UserDevice.objects.filter(is_active=True).count())"
python manage.py shell -c "from notifications.models import *; print(Notification.objects.filter(is_read=False).count())"
```
