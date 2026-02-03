# Notifications API Documentation

Push notification system using Firebase Cloud Messaging (FCM).

Base URL: `/api/v1/notifications/`

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      API Layer                          │
│                     (views.py)                          │
│   Device Tokens | Notifications | Preferences | Test    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Service Layer                         │
│                                                         │
│  ┌─────────────────────┐    ┌─────────────────────┐    │
│  │ NotificationService │    │     FCMService      │    │
│  │  (High-level)       │───▶│    (Low-level)      │    │
│  │                     │    │                     │    │
│  │ • notify_user       │    │ • Firebase init     │    │
│  │ • send_notification │    │ • send_to_token     │    │
│  │ • register_device   │    │ • send_to_multiple  │    │
│  └─────────────────────┘    └─────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                           │
│                    (models.py)                          │
│                                                         │
│  DeviceToken | NotificationType | Notification |        │
│              NotificationPreference                     │
└─────────────────────────────────────────────────────────┘
```

---

## Notification Flow

```
1. Event occurs (e.g., QC pending)
           │
           ▼
2. Call NotificationService.notify_user()
           │
           ▼
3. Lookup NotificationType → Get template
           │
           ▼
4. Render title/body with context
           │
           ▼
5. For the user:
   ├── Check NotificationPreference (is enabled?)
   ├── Create Notification record
   ├── Get user's DeviceTokens (all devices)
   └── Call FCMService.send_to_multiple()
           │
           ▼
6. Update Notification status (SENT/FAILED)
           │
           ▼
7. User receives push notification on ALL registered devices
```

---

## Setup

### Backend Dependencies

```bash
pip install firebase-admin
```

### Firebase Configuration

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Project Settings → Service Accounts → Generate new private key
3. Save JSON file as `config/credentials.json`

### Frontend Dependencies

| Platform | Package |
|----------|---------|
| Android | `com.google.firebase:firebase-messaging` |
| iOS | `Firebase/Messaging` (CocoaPods) |
| Web | `firebase` (npm) |

---

## Quick Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST/DELETE | `/device-tokens/` | Manage device tokens |
| GET | `/` | List notifications |
| GET | `/{id}/` | Get notification detail |
| POST | `/mark-read/` | Mark notifications as read |
| GET | `/unread-count/` | Get unread count |
| GET/POST | `/preferences/` | Manage notification preferences |
| POST | `/test/` | Test FCM (development only) |

---

## Testing with Postman (Complete Guide)

### Prerequisites Checklist

| Item | Status |
|------|--------|
| Django server running | `python manage.py runserver` |
| Firebase credentials | `config/credentials.json` exists |
| Firebase project | Created at console.firebase.google.com |
| VAPID key | Generated in Firebase Console |

---

### Step 1: Start Django Server

```bash
python manage.py runserver
```

Server will run at `http://localhost:8000`

---

### Step 2: Get JWT Token (Login)

**Request:**
```
POST http://localhost:8000/api/v1/accounts/login/
Content-Type: application/json

{
    "email": "your_email@example.com",
    "password": "your_password"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1...",
    "refresh": "eyJ0eXAiOiJKV1..."
}
```

Save the `access` token for all subsequent requests.

---

### Step 3: Get FCM Token from Frontend

You need an FCM token from your frontend app. Here's how to get it:

#### For React (Web):

1. Install Firebase:
```bash
npm install firebase
```

2. Create `src/firebase.js`:
```javascript
import { initializeApp } from 'firebase/app';
import { getMessaging, getToken } from 'firebase/messaging';

const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "your-sender-id",
  appId: "your-app-id"
};

const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

export { messaging, getToken };
```

3. Get the token (add this to any component temporarily):
```javascript
import { messaging, getToken } from './firebase';

// Call this function and check browser console
const getFCMToken = async () => {
  const token = await getToken(messaging, {
    vapidKey: 'your-vapid-key-from-firebase-console'
  });
  console.log('FCM Token:', token);  // Copy this!
};

getFCMToken();
```

4. **Important:** Allow notifications when browser prompts

5. Copy the token from browser console (F12 → Console)

#### For Android:
```kotlin
FirebaseMessaging.getInstance().token.addOnSuccessListener { token ->
    Log.d("FCM", "Token: $token")  // Copy from Logcat
}
```

#### For iOS:
```swift
Messaging.messaging().token { token, error in
    if let token = token {
        print("FCM Token: \(token)")  // Copy from Xcode console
    }
}
```

---

### Step 4: Register Device Token

**Request:**
```
POST http://localhost:8000/api/v1/notifications/device-tokens/
Authorization: Bearer <jwt_access_token>
Content-Type: application/json

{
    "token": "<fcm_token_from_step_3>",
    "platform": "WEB",
    "device_name": "Chrome Browser"
}
```

**Platform options:** `ANDROID`, `IOS`, `WEB`

**Response:** `201 Created`
```json
{
    "id": 1,
    "token": "your_fcm_token...",
    "platform": "WEB",
    "device_name": "Chrome Browser",
    "is_active": true,
    "created_at": "2025-01-15T10:30:00Z",
    "last_used_at": "2025-01-15T10:30:00Z"
}
```

---

### Step 5: Send Test Push Notification

**Request:**
```
POST http://localhost:8000/api/v1/notifications/test/
Authorization: Bearer <jwt_access_token>
Content-Type: application/json

{
    "token": "<fcm_token_from_step_3>",
    "title": "Test Notification",
    "body": "Hello from Factory App!"
}
```

**Success Response:** `200 OK`
```json
{
    "success": true,
    "message_id": "projects/your-project/messages/0:1234567890",
    "error": null
}
```

**You should receive a push notification on your device/browser!**

**Error Response:** `400 Bad Request`
```json
{
    "success": false,
    "message_id": null,
    "error": "Requested entity was not found."
}
```

---

### Step 6: List Notifications

**Request:**
```
GET http://localhost:8000/api/v1/notifications/
Authorization: Bearer <jwt_access_token>
Company-Code: JIVO_OIL
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| is_read | boolean | Filter by read status (`true`/`false`) |
| limit | integer | Results per page (default: 50) |
| offset | integer | Pagination offset |

**Example with filters:**
```
GET http://localhost:8000/api/v1/notifications/?is_read=false&limit=10
```

**Response:**
```json
{
    "count": 25,
    "unread_count": 5,
    "results": [
        {
            "id": 1,
            "type_code": "RAW_MATERIAL_GATEIN",
            "title": "New Material Arrival",
            "body": "Vehicle KA-01-AB-1234 has arrived",
            "is_read": false,
            "created_at": "2025-01-15T10:30:00Z"
        }
    ]
}
```

---

### Step 7: Get Notification Detail

**Request:**
```
GET http://localhost:8000/api/v1/notifications/1/
Authorization: Bearer <jwt_access_token>
Company-Code: JIVO_OIL
```

**Response:**
```json
{
    "id": 1,
    "notification_type": {
        "id": 1,
        "code": "RAW_MATERIAL_GATEIN",
        "name": "Raw Material Gate In",
        "description": "",
        "is_active": true
    },
    "title": "New Material Arrival",
    "body": "Vehicle KA-01-AB-1234 has arrived",
    "data": {"vehicle_number": "KA-01-AB-1234"},
    "status": "SENT",
    "is_read": true,
    "read_at": "2025-01-15T11:00:00Z",
    "created_at": "2025-01-15T10:30:00Z"
}
```

**Note:** Automatically marks notification as read.

---

### Step 8: Mark Notifications as Read

**Mark specific notifications:**
```
POST http://localhost:8000/api/v1/notifications/mark-read/
Authorization: Bearer <jwt_access_token>
Company-Code: JIVO_OIL
Content-Type: application/json

{
    "notification_ids": [1, 2, 3]
}
```

**Mark all as read:**
```json
{
    "notification_ids": []
}
```

**Response:**
```json
{
    "message": "3 notification(s) marked as read"
}
```

---

### Step 9: Get Unread Count

**Request:**
```
GET http://localhost:8000/api/v1/notifications/unread-count/
Authorization: Bearer <jwt_access_token>
```

**Response:**
```json
{
    "unread_count": 5
}
```

---

### Step 10: Manage Preferences

**Get all preferences:**
```
GET http://localhost:8000/api/v1/notifications/preferences/
Authorization: Bearer <jwt_access_token>
```

**Response:**
```json
[
    {
        "id": 1,
        "code": "QC_PENDING",
        "name": "QC Pending",
        "description": "Notification when QC is required",
        "is_enabled": true
    },
    {
        "id": 2,
        "code": "RAW_MATERIAL_GATEIN",
        "name": "Raw Material Gate In",
        "description": "",
        "is_enabled": false
    }
]
```

**Disable a notification type:**
```
POST http://localhost:8000/api/v1/notifications/preferences/
Authorization: Bearer <jwt_access_token>
Content-Type: application/json

{
    "notification_type_id": 2,
    "is_enabled": false
}
```

---

### Step 11: List Registered Devices

**Request:**
```
GET http://localhost:8000/api/v1/notifications/device-tokens/
Authorization: Bearer <jwt_access_token>
```

**Response:**
```json
[
    {
        "id": 1,
        "token": "abc123...",
        "platform": "WEB",
        "device_name": "Chrome Browser",
        "is_active": true,
        "created_at": "2025-01-15T10:30:00Z",
        "last_used_at": "2025-01-15T10:30:00Z"
    },
    {
        "id": 2,
        "token": "xyz789...",
        "platform": "ANDROID",
        "device_name": "Samsung S21",
        "is_active": true,
        "created_at": "2025-01-14T09:00:00Z",
        "last_used_at": "2025-01-15T08:00:00Z"
    }
]
```

---

### Step 12: Unregister Device

**Request:**
```
DELETE http://localhost:8000/api/v1/notifications/device-tokens/
Authorization: Bearer <jwt_access_token>
Content-Type: application/json

{
    "token": "<fcm_token_to_remove>"
}
```

**Response:**
```json
{
    "message": "Device token unregistered"
}
```

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `TOKEN_UNREGISTERED` | FCM token is invalid/expired | Get new token from frontend and re-register |
| `Requested entity was not found` | Invalid FCM token | Check token is correct, get fresh token |
| `No active device tokens` | User has no registered devices | Register device token first |
| `Notification type not found` | Invalid notification code | Check `NotificationTypeCode` enum |
| `401 Unauthorized` | Invalid/expired JWT token | Login again to get new token |
| `Company-Code header is missing` | Missing header | Add `Company-Code: JIVO_OIL` header |

### Browser Notification Not Showing?

1. Check browser notification permission (should be "Allow")
2. Check if browser supports notifications
3. For Chrome: Check `chrome://settings/content/notifications`
4. Try with browser in foreground and background

### FCM Token Issues?

1. Make sure Firebase is properly configured in frontend
2. VAPID key must match your Firebase project
3. Service worker must be registered (for web)
4. Token expires - always get fresh token on app start

---

## Usage in Code

### Send Notification to User

```python
from notifications.services import NotificationService
from notifications.enums import NotificationTypeCode

NotificationService.notify_user(
    notification_type_code=NotificationTypeCode.QC_PENDING,
    company=company,
    user=user,
    context={
        "vehicle_number": "KA-01-AB-1234",
        "material": "Sunflower Oil"
    }
)
```

### Send Notification to Multiple Users

```python
NotificationService.send_notification(
    notification_type_code=NotificationTypeCode.QC_PENDING,
    company=company,
    recipients=[user1, user2, user3],
    context={
        "vehicle_number": "KA-01-AB-1234",
        "material": "Sunflower Oil"
    }
)
```

### Direct FCM Send (Low-level)

```python
from notifications.services.fcm_service import FCMService

# Single device
result = FCMService.send_to_token(
    token="device_token",
    title="Alert",
    body="Message body",
    data={"key": "value"}
)

# Multiple devices
result = FCMService.send_to_multiple(
    tokens=["token1", "token2"],
    title="Alert",
    body="Message body"
)
```

---

## Notification Types

| Code | Description |
|------|-------------|
| `PERSON_ENTRY` | Person entered through gate |
| `PERSON_EXIT` | Person exited through gate |
| `LONG_DURATION_ALERT` | Person stayed beyond allowed time |
| `BLACKLISTED_PERSON` | Blacklisted person attempted entry |
| `VEHICLE_ENTRY` | Vehicle entered through gate |
| `VEHICLE_EXIT` | Vehicle exited through gate |
| `RAW_MATERIAL_GATEIN` | Raw material vehicle gate-in |
| `DAILY_NEEDS_GATEIN` | Daily needs vehicle gate-in |
| `MAINTENANCE_GATEIN` | Maintenance vehicle gate-in |
| `CONSTRUCTION_GATEIN` | Construction vehicle gate-in |
| `QC_PENDING` | Quality check pending |
| `QC_COMPLETED` | Quality check completed |
| `QC_FAILED` | Quality check failed |
| `WEIGHMENT_COMPLETED` | Weighment completed |
| `SECURITY_ALERT` | Security alert raised |

---

## Models

### DeviceToken
| Field | Description |
|-------|-------------|
| user | User who owns this device |
| company | Optional company scope |
| token | FCM token (unique) |
| platform | `ANDROID`, `IOS`, `WEB` |
| is_active | Token validity status |

### NotificationType
| Field | Description |
|-------|-------------|
| code | Unique code (e.g., `QC_PENDING`) |
| name | Human readable name |
| title_template | Template like `"QC Pending for {vehicle_number}"` |
| body_template | Message body template |
| is_active | Enable/disable notification type |

### Notification
| Field | Description |
|-------|-------------|
| recipient | User who received it |
| company | Company context |
| title/body | Rendered message |
| status | `PENDING`, `SENT`, `FAILED`, `DELIVERED` |
| is_read | Read status |

### NotificationPreference
| Field | Description |
|-------|-------------|
| user | User |
| notification_type | Type of notification |
| is_enabled | Opt-in/opt-out status |

---

## Multi-Device Support

When a user registers multiple devices, notifications are sent to **ALL** devices:

```
User: john@example.com
├── Phone (Android)  → ✓ receives notification
├── Tablet (iOS)     → ✓ receives notification
└── Browser (Web)    → ✓ receives notification
```

---

## Files Summary

| File | Purpose |
|------|---------|
| `models.py` | Database models |
| `views.py` | API endpoints |
| `urls.py` | URL routing |
| `serializers.py` | Request/response serialization |
| `services/fcm_service.py` | Firebase communication |
| `services/notification_service.py` | Business logic |
| `enums.py` | Notification type codes |
| `admin.py` | Django admin configuration |

---

## Authentication

All endpoints require JWT authentication.

```
Authorization: Bearer <access_token>
```

Some endpoints also require company context:
```
Company-Code: JIVO_OIL
```

---

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
