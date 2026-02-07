# Notifications - Permissions Documentation

---

## Permission Classes

| Class                    | Code                                        | Used In             |
|--------------------------|---------------------------------------------|---------------------|
| `CanSendNotification`    | `notifications.can_send_notification`        | `SendNotificationAPI` |
| `CanSendBulkNotification`| `notifications.can_send_bulk_notification`   | (reserved for future) |

---

## API Permission Matrix

| Endpoint                          | Method | Permissions                                                      |
|-----------------------------------|--------|------------------------------------------------------------------|
| `/devices/register/`              | POST   | `IsAuthenticated`                                                |
| `/devices/unregister/`            | POST   | `IsAuthenticated`                                                |
| `/`                               | GET    | `IsAuthenticated`                                                |
| `/mark-read/`                     | POST   | `IsAuthenticated`                                                |
| `/unread-count/`                  | GET    | `IsAuthenticated`                                                |
| `/send/`                          | POST   | `IsAuthenticated` + `HasCompanyContext` + `CanSendNotification`  |

---

## Permission Details

### IsAuthenticated (all endpoints)
- User must have a valid JWT access token in the `Authorization: Bearer <token>` header.
- No specific Django permission required.

### HasCompanyContext (send endpoint only)
- Request must include `Company-Code` header with a valid company code.
- The authenticated user must have an active `UserCompany` record for that company.
- On success, `request.company` is populated with the `UserCompany` instance.

### CanSendNotification
- Django permission: `notifications.can_send_notification`
- Required to send manual notifications via the `/send/` endpoint.
- Assigned via the **"Notification Sender"** group (created by migration `0002_create_notification_groups`).

### CanSendBulkNotification
- Django permission: `notifications.can_send_bulk_notification`
- Reserved for future bulk operations that need separate access control.
- Also assigned via the **"Notification Sender"** group.

---

## Permission Group

### Notification Sender

Created automatically by data migration `0002_create_notification_groups.py`.

| Group Name           | Permissions Included                                                     |
|----------------------|--------------------------------------------------------------------------|
| `Notification Sender`| `notifications.can_send_notification`, `notifications.can_send_bulk_notification` |

### How to Assign

**Via Django Admin:**
1. Go to `/admin/auth/user/<user_id>/change/`
2. Scroll to **Groups** section
3. Add the user to **"Notification Sender"** group
4. Save

**Via Django Shell:**
```python
from django.contrib.auth.models import Group
from accounts.models import User

user = User.objects.get(email="admin@example.com")
group = Group.objects.get(name="Notification Sender")
user.groups.add(group)
```

**Via Data Migration (for default admin users):**
```python
def assign_notification_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    User = apps.get_model("accounts", "User")

    group = Group.objects.get(name="Notification Sender")
    admins = User.objects.filter(is_staff=True)
    for admin in admins:
        admin.groups.add(group)
```

---

## Default Django Permissions

In addition to custom permissions, Django auto-creates these for each model:

### UserDevice
| Permission                        | Description            |
|-----------------------------------|------------------------|
| `notifications.add_userdevice`    | Can add user device    |
| `notifications.change_userdevice` | Can change user device |
| `notifications.delete_userdevice` | Can delete user device |
| `notifications.view_userdevice`   | Can view user device   |

### Notification
| Permission                         | Description             |
|------------------------------------|-------------------------|
| `notifications.add_notification`   | Can add notification    |
| `notifications.change_notification`| Can change notification |
| `notifications.delete_notification`| Can delete notification |
| `notifications.view_notification`  | Can view notification   |

These default permissions are used by Django Admin only. API access is controlled by the custom permission classes listed above.

---

## Data Flow — Who Can Do What

| Action                           | Who Can Do It                        |
|----------------------------------|--------------------------------------|
| Register their own device token  | Any authenticated user               |
| Unregister their own device token| Any authenticated user               |
| View their own notifications     | Any authenticated user               |
| Mark their own notifications read| Any authenticated user               |
| Get their own unread count       | Any authenticated user               |
| Send manual notification         | Users with `can_send_notification`   |
| Auto-triggered notifications     | System (via signals, no permission needed) |
