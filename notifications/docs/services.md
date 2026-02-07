# Notifications - Service Layer Documentation

All notification logic is in `notifications/services.py` via the `NotificationService` class.

---

## Firebase Initialization

```python
from notifications.services import get_firebase_app

app = get_firebase_app()  # lazy singleton, initialized once
```

- Uses `firebase-admin` Python SDK
- Reads credentials from `settings.FCM_CREDENTIALS_PATH` (default: `firebase-service-account.json`)
- Initialized lazily on first use (not at import time)

---

## NotificationService Methods

### register_device()

Register or update an FCM device token for a user.

```python
NotificationService.register_device(
    user=user,
    fcm_token="dGVzdC10b2tlbi...",
    device_type="WEB",         # WEB | ANDROID | IOS
    device_info="Chrome/120"   # optional
)
```

**Behavior:**
- If `fcm_token` already exists for a **different** user, the old record is deleted (token reassignment)
- If `fcm_token` already exists for the **same** user, the record is updated
- If `fcm_token` is new, a new `UserDevice` record is created
- Returns the `UserDevice` instance

---

### unregister_device()

Remove an FCM token for a user. Call on logout.

```python
removed = NotificationService.unregister_device(
    user=user,
    fcm_token="dGVzdC10b2tlbi..."
)
# removed = True if token was found and deleted
```

---

### cleanup_stale_tokens()

Remove device tokens not used in N days. Used by the management command.

```python
count = NotificationService.cleanup_stale_tokens(days=30)
# Returns number of deleted tokens
```

---

### send_notification_to_user()

Send notification to a single user across all their active devices.

```python
notification = NotificationService.send_notification_to_user(
    user=user,
    title="GRPO Posted",
    body="GRPO for PO 4500001234 posted. SAP Doc: 50000123",
    notification_type="GRPO_POSTED",
    click_action_url="/grpo/5",
    reference_type="grpo_posting",
    reference_id=5,
    company=company_instance,       # optional
    extra_data={"key": "value"},    # optional
    created_by=admin_user,          # optional
)
```

**What it does:**
1. Creates a `Notification` record in the database (in-app notification center)
2. Fetches all active `UserDevice` tokens for the user
3. Sends an FCM push notification to each token
4. If a token returns `UnregisteredError`, auto-deactivates it (`is_active=False`)
5. Returns the `Notification` instance

**Transaction:** Runs inside `@transaction.atomic` — if DB creation fails, no FCM is sent.

---

### send_notification_to_group()

Send the same notification to multiple users.

```python
notifications = NotificationService.send_notification_to_group(
    users=[user1, user2, user3],
    title="System Update",
    body="The system will be upgraded tonight.",
    notification_type="GENERAL_ANNOUNCEMENT",
    click_action_url="/announcements",
    company=company_instance,
    created_by=admin_user,
)
# Returns list of Notification instances
```

**Behavior:** Iterates and calls `send_notification_to_user()` for each user.

---

### send_bulk_notification()

Send notification to all active users in a company. Optionally filter by role.

```python
count = NotificationService.send_bulk_notification(
    company=company_instance,
    title="Maintenance Notice",
    body="Plant maintenance scheduled for Feb 10.",
    notification_type="GENERAL_ANNOUNCEMENT",
    click_action_url="/announcements",
    role_name="QC",            # optional — filter by UserRole name
    created_by=admin_user,     # optional
)
# Returns count of recipients
```

**Behavior:**
1. Queries `UserCompany` for all active users in the company
2. Optionally filters by `role__name`
3. Calls `send_notification_to_group()` for the filtered user list

---

## FCM Message Structure

Every push notification sent to a device contains:

```python
messaging.Message(
    notification=messaging.Notification(
        title="Weighment Recorded",
        body="Weighment recorded for RM-2026-0001. Net: 2500.000 kg.",
    ),
    data={
        "notification_id": "42",
        "notification_type": "WEIGHMENT_RECORDED",
        "reference_type": "vehicle_entry",
        "reference_id": "10",
        "click_action_url": "/gate-entries/10",
    },
    token="<fcm_device_token>",
    webpush=WebpushConfig(
        fcm_options=WebpushFCMOptions(link="/gate-entries/10"),
        notification=WebpushNotification(
            title="Weighment Recorded",
            body="Weighment recorded for RM-2026-0001. Net: 2500.000 kg.",
            icon="/icons/notification-icon.png",
        ),
    ),
)
```

- `notification` — shown by browser as push notification
- `data` — custom key-value data accessible by service worker and frontend
- `webpush` — web-specific configuration including the click link and icon

---

## Stale Token Handling

| Scenario                        | Action                                      |
|---------------------------------|---------------------------------------------|
| FCM returns `UnregisteredError` | Token marked `is_active=False` immediately  |
| Token unused for 30+ days       | Deleted by `cleanup_stale_tokens()` command |
| Same token, new user login      | Old user's record deleted, new record created |

---

## Usage from Django Shell

```python
from notifications.services import NotificationService
from accounts.models import User

user = User.objects.get(email="admin@example.com")

# Send a test notification
NotificationService.send_notification_to_user(
    user=user,
    title="Test from Shell",
    body="This is a test notification from Django shell.",
    click_action_url="/dashboard",
)
```

---

## Management Command

```bash
# Remove tokens not used in 30 days (default)
python manage.py cleanup_stale_fcm_tokens

# Remove tokens not used in 7 days
python manage.py cleanup_stale_fcm_tokens --days 7
```
