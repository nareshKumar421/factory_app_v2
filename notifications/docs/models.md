# Notifications - Models Documentation

---

## 1. UserDevice

Stores Firebase Cloud Messaging (FCM) tokens for each user's device/browser. Supports multi-device login — one user can have multiple active tokens.

### Table: `notifications_userdevice`

| Column        | Type          | Constraints          | Description                              |
|---------------|---------------|----------------------|------------------------------------------|
| `id`          | BigAutoField  | PK, auto             | Primary key                              |
| `user_id`     | ForeignKey    | NOT NULL, CASCADE    | Link to `accounts.User`                  |
| `fcm_token`   | TextField     | UNIQUE               | FCM registration token from browser/device |
| `device_type` | CharField(20) | NOT NULL, default `WEB` | One of: `WEB`, `ANDROID`, `IOS`       |
| `device_info` | CharField(255)| blank                | Browser user-agent or device description |
| `is_active`   | BooleanField  | default `True`       | False when token is stale/expired        |
| `created_at`  | DateTimeField | auto_now_add         | When device was first registered         |
| `last_used_at`| DateTimeField | auto_now             | Updated each time record is touched      |

### Relationships

```
accounts.User (1) ──── (N) UserDevice
```

- One user can have many devices (multi-device login)
- `related_name="fcm_devices"` — access via `user.fcm_devices.all()`

### Indexes

- `fcm_token` (unique index)
- Ordering: `-last_used_at` (most recently used first)

---

## 2. NotificationType

TextChoices enum for notification categorization.

| Value                       | Label                       | Triggered By                   |
|-----------------------------|-----------------------------|--------------------------------|
| `GATE_ENTRY_CREATED`        | Gate Entry Created          | VehicleEntry post_save (created) |
| `GATE_ENTRY_STATUS_CHANGED` | Gate Entry Status Changed   | (reserved)                     |
| `SECURITY_CHECK_DONE`       | Security Check Completed    | (reserved)                     |
| `WEIGHMENT_RECORDED`        | Weighment Recorded          | Weighment post_save (created)  |
| `ARRIVAL_SLIP_SUBMITTED`    | Arrival Slip Submitted      | MaterialArrivalSlip post_save  |
| `QC_INSPECTION_SUBMITTED`   | QC Inspection Submitted     | RawMaterialInspection post_save |
| `QC_CHEMIST_APPROVED`       | QC Chemist Approved         | RawMaterialInspection post_save |
| `QC_QAM_APPROVED`           | QC QAM Approved             | RawMaterialInspection post_save |
| `QC_REJECTED`               | QC Rejected                 | (reserved)                     |
| `QC_COMPLETED`              | QC Completed                | (reserved)                     |
| `GRPO_POSTED`               | GRPO Posted to SAP          | GRPOPosting post_save          |
| `GRPO_FAILED`               | GRPO Posting Failed         | GRPOPosting post_save          |
| `GENERAL_ANNOUNCEMENT`      | General Announcement        | Manual via admin API           |

---

## 3. Notification

Stores notifications for the in-app notification center. Each record represents one notification to one user.

### Table: `notifications_notification`

| Column              | Type          | Constraints          | Description                                 |
|---------------------|---------------|----------------------|---------------------------------------------|
| `id`                | BigAutoField  | PK, auto             | Primary key                                 |
| `recipient_id`      | ForeignKey    | NOT NULL, CASCADE    | User who receives the notification          |
| `company_id`        | ForeignKey    | NULL, CASCADE        | Company context (null = global notification)|
| `title`             | CharField(255)| NOT NULL             | Notification title                          |
| `body`              | TextField     | NOT NULL             | Notification body text                      |
| `notification_type` | CharField(50) | NOT NULL, default `GENERAL_ANNOUNCEMENT` | One of `NotificationType` values |
| `click_action_url`  | CharField(500)| blank                | Frontend route to navigate on click         |
| `reference_type`    | CharField(50) | blank                | Entity type: `vehicle_entry`, `inspection`, etc. |
| `reference_id`      | IntegerField  | NULL                 | ID of the referenced entity                 |
| `is_read`           | BooleanField  | default `False`      | Whether user has read this notification     |
| `read_at`           | DateTimeField | NULL                 | Timestamp when marked as read               |
| `extra_data`        | JSONField     | default `{}`         | Additional key-value data                   |
| `created_at`        | DateTimeField | auto_now_add         | When notification was created               |
| `created_by_id`     | ForeignKey    | NULL, SET_NULL       | User who triggered/sent the notification    |

### Relationships

```
accounts.User (1) ──── (N) Notification (as recipient)
accounts.User (1) ──── (N) Notification (as created_by)
company.Company (1) ── (N) Notification
```

- `related_name="notifications"` — `user.notifications.all()` for received
- `related_name="notifications_sent"` — `user.notifications_sent.all()` for sent
- `related_name="notifications"` — `company.notifications.all()`

### Indexes

| Index                                  | Purpose                                  |
|----------------------------------------|------------------------------------------|
| `(recipient_id, -created_at)`          | Fast user notification listing           |
| `(recipient_id, is_read)`              | Fast unread count queries                |
| `(notification_type)`                  | Fast type-based filtering                |

### Custom Permissions

| Codename                  | Description                        |
|---------------------------|------------------------------------|
| `can_send_notification`   | Can send manual notifications      |
| `can_send_bulk_notification` | Can send bulk/broadcast notifications |

---

## Entity Relationship Diagram

```
accounts.User
    |
    |── (1:N) ── UserDevice
    |               ├── fcm_token (unique)
    |               ├── device_type
    |               └── is_active
    |
    |── (1:N) ── Notification (as recipient)
    |               ├── title, body
    |               ├── notification_type
    |               ├── click_action_url
    |               ├── reference_type + reference_id
    |               ├── is_read, read_at
    |               └── extra_data (JSON)
    |
    └── (1:N) ── Notification (as created_by)

company.Company
    |
    └── (1:N) ── Notification (company context)
```

---

## Deep Linking Fields

The `click_action_url`, `reference_type`, and `reference_id` fields work together for deep linking:

| reference_type   | reference_id points to          | click_action_url pattern            |
|------------------|---------------------------------|-------------------------------------|
| `vehicle_entry`  | `VehicleEntry.id`               | `/gate-entries/{id}`                |
| `arrival_slip`   | `MaterialArrivalSlip.id`        | `/gate-entries/{entry_id}/qc`       |
| `inspection`     | `RawMaterialInspection.id`      | `/gate-entries/{entry_id}/qc/{id}`  |
| `grpo_posting`   | `GRPOPosting.id`                | `/grpo/{id}`                        |
| (empty)          | null                            | `/notifications`                    |
