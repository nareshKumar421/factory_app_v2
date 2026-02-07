# Notifications API Documentation

Base URL: `/api/v1/notifications/`

---

## 1. Register Device Token

Register an FCM device token for push notifications. Call this after login.

- **URL**: `POST /api/v1/notifications/devices/register/`
- **Auth**: `Bearer <access_token>`
- **Permission**: `IsAuthenticated`

### Request Body

| Field         | Type   | Required | Default | Description                        |
|---------------|--------|----------|---------|------------------------------------|
| `fcm_token`   | string | Yes      | -       | Firebase Cloud Messaging token     |
| `device_type` | string | No       | `"WEB"` | One of: `WEB`, `ANDROID`, `IOS`    |
| `device_info` | string | No       | `""`    | Browser user-agent or device info  |

### Example Request

```json
POST /api/v1/notifications/devices/register/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi...
Content-Type: application/json

{
    "fcm_token": "dGVzdC10b2tlbi0xMjM0NTY3ODkw...",
    "device_type": "WEB",
    "device_info": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120"
}
```

### Success Response — `201 Created`

```json
{
    "message": "Device registered successfully",
    "device_id": 12
}
```

### Behavior Notes

- If the same `fcm_token` was previously registered by a different user, it gets reassigned to the current user (browser can only belong to one user at a time).
- If the token already exists for the same user, its `device_type` and `device_info` are updated.

---

## 2. Unregister Device Token

Remove an FCM token. Call this before logout to stop push notifications on the current device.

- **URL**: `POST /api/v1/notifications/devices/unregister/`
- **Auth**: `Bearer <access_token>`
- **Permission**: `IsAuthenticated`

### Request Body

| Field       | Type   | Required | Description                    |
|-------------|--------|----------|--------------------------------|
| `fcm_token` | string | Yes      | FCM token to unregister        |

### Example Request

```json
POST /api/v1/notifications/devices/unregister/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi...
Content-Type: application/json

{
    "fcm_token": "dGVzdC10b2tlbi0xMjM0NTY3ODkw..."
}
```

### Success Response — `200 OK`

```json
{
    "message": "Device unregistered successfully"
}
```

### Error Response — `404 Not Found`

```json
{
    "detail": "Device token not found"
}
```

---

## 3. List Notifications

Retrieve paginated notifications for the authenticated user.

- **URL**: `GET /api/v1/notifications/`
- **Auth**: `Bearer <access_token>`
- **Permission**: `IsAuthenticated`

### Query Parameters

| Param       | Type    | Default | Description                                       |
|-------------|---------|---------|---------------------------------------------------|
| `is_read`   | string  | -       | Filter: `"true"` or `"false"`                     |
| `type`      | string  | -       | Filter by notification type (e.g., `GRPO_POSTED`) |
| `page`      | integer | `1`     | Page number                                       |
| `page_size` | integer | `20`    | Results per page (max 100)                        |

### Optional Header

| Header         | Description                                                 |
|----------------|-------------------------------------------------------------|
| `Company-Code` | If provided, filters to notifications for that company + global notifications |

### Example Request

```
GET /api/v1/notifications/?is_read=false&page=1&page_size=10
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi...
Company-Code: JIVO_OIL
```

### Success Response — `200 OK`

```json
{
    "results": [
        {
            "id": 42,
            "title": "GRPO Posted Successfully",
            "body": "GRPO for PO 4500001234 posted. SAP Doc: 50000123",
            "notification_type": "GRPO_POSTED",
            "click_action_url": "/grpo/5",
            "reference_type": "grpo_posting",
            "reference_id": 5,
            "is_read": false,
            "read_at": null,
            "extra_data": {},
            "created_at": "2026-02-07T15:30:00+05:30"
        },
        {
            "id": 41,
            "title": "Weighment Recorded",
            "body": "Weighment recorded for RM-2026-0001. Net: 2500.000 kg.",
            "notification_type": "WEIGHMENT_RECORDED",
            "click_action_url": "/gate-entries/10",
            "reference_type": "vehicle_entry",
            "reference_id": 10,
            "is_read": false,
            "read_at": null,
            "extra_data": {},
            "created_at": "2026-02-07T14:15:00+05:30"
        }
    ],
    "total_count": 25,
    "unread_count": 8,
    "page": 1,
    "page_size": 10
}
```

---

## 4. Mark Notifications as Read

Mark specific notifications or all as read.

- **URL**: `POST /api/v1/notifications/mark-read/`
- **Auth**: `Bearer <access_token>`
- **Permission**: `IsAuthenticated`

### Request Body

| Field              | Type     | Required | Default | Description                                        |
|--------------------|----------|----------|---------|----------------------------------------------------|
| `notification_ids` | int[]    | No       | `[]`    | Specific IDs to mark read. Empty = mark ALL as read |

### Example — Mark Specific

```json
POST /api/v1/notifications/mark-read/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi...
Content-Type: application/json

{
    "notification_ids": [41, 42]
}
```

### Example — Mark All as Read

```json
POST /api/v1/notifications/mark-read/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi...
Content-Type: application/json

{}
```

### Success Response — `200 OK`

```json
{
    "marked_read": 2
}
```

---

## 5. Get Unread Count

Get the total number of unread notifications for the authenticated user.

- **URL**: `GET /api/v1/notifications/unread-count/`
- **Auth**: `Bearer <access_token>`
- **Permission**: `IsAuthenticated`

### Example Request

```
GET /api/v1/notifications/unread-count/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi...
```

### Success Response — `200 OK`

```json
{
    "unread_count": 8
}
```

---

## 6. Send Notification (Admin)

Manually send a notification to specific users or broadcast to entire company.

- **URL**: `POST /api/v1/notifications/send/`
- **Auth**: `Bearer <access_token>`
- **Headers**: `Company-Code: <code>` (required)
- **Permission**: `IsAuthenticated` + `HasCompanyContext` + `CanSendNotification`

### Request Body

| Field                | Type     | Required | Default                | Description                                          |
|----------------------|----------|----------|------------------------|------------------------------------------------------|
| `title`              | string   | Yes      | -                      | Notification title                                   |
| `body`               | string   | Yes      | -                      | Notification body text                               |
| `notification_type`  | string   | No       | `GENERAL_ANNOUNCEMENT` | See notification types below                         |
| `click_action_url`   | string   | No       | `""`                   | Frontend route for click redirect                    |
| `recipient_user_ids` | int[]    | No       | `[]`                   | Specific user IDs. Empty = broadcast to all in company |
| `role_filter`        | string   | No       | `""`                   | Filter recipients by role (only when broadcasting)   |

### Example — Send to Specific Users

```json
POST /api/v1/notifications/send/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi...
Company-Code: JIVO_OIL
Content-Type: application/json

{
    "title": "Maintenance Scheduled",
    "body": "Plant maintenance on Feb 10, 2026. Gate entry suspended 6AM-12PM.",
    "notification_type": "GENERAL_ANNOUNCEMENT",
    "click_action_url": "/announcements",
    "recipient_user_ids": [1, 5, 12]
}
```

### Example — Broadcast to All Company Users

```json
POST /api/v1/notifications/send/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi...
Company-Code: JIVO_OIL
Content-Type: application/json

{
    "title": "System Update",
    "body": "The system will be upgraded tonight at 11 PM IST.",
    "notification_type": "GENERAL_ANNOUNCEMENT"
}
```

### Example — Broadcast to Specific Role

```json
POST /api/v1/notifications/send/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi...
Company-Code: JIVO_OIL
Content-Type: application/json

{
    "title": "QC Report Due",
    "body": "Pending inspections must be completed by EOD.",
    "notification_type": "GENERAL_ANNOUNCEMENT",
    "click_action_url": "/quality-control",
    "role_filter": "QC"
}
```

### Success Response — `200 OK`

```json
{
    "message": "Notification sent to 15 users",
    "recipients_count": 15
}
```

---

## Notification Types

| Type                        | Description                  | Auto-Triggered |
|-----------------------------|------------------------------|----------------|
| `GATE_ENTRY_CREATED`        | New gate entry created       | Yes            |
| `GATE_ENTRY_STATUS_CHANGED` | Gate entry status updated    | Yes            |
| `SECURITY_CHECK_DONE`       | Security check completed     | Yes            |
| `WEIGHMENT_RECORDED`        | Weighment recorded           | Yes            |
| `ARRIVAL_SLIP_SUBMITTED`    | Arrival slip submitted to QC | Yes            |
| `QC_INSPECTION_SUBMITTED`   | QC inspection submitted      | Yes            |
| `QC_CHEMIST_APPROVED`       | QA Chemist approved          | Yes            |
| `QC_QAM_APPROVED`           | QAM approved                 | Yes            |
| `QC_REJECTED`               | QC inspection rejected       | Yes            |
| `QC_COMPLETED`              | QC process completed         | Yes            |
| `GRPO_POSTED`               | GRPO posted to SAP           | Yes            |
| `GRPO_FAILED`               | GRPO posting failed          | Yes            |
| `GENERAL_ANNOUNCEMENT`      | Manual announcement          | No (admin only)|

---

## Error Responses

All endpoints return standard DRF error format:

### 401 Unauthorized

```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden (Missing Company-Code)

```json
{
    "detail": "Company-Code header is missing."
}
```

### 403 Forbidden (Missing Permission)

```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 400 Bad Request (Validation Error)

```json
{
    "fcm_token": ["This field is required."]
}
```
