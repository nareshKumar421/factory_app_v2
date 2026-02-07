# Firebase Notification System - Setup Guide

> **Project**: Sampurn Factory App (Jivo Wellness)
> **Backend**: Django 6.0.1 + Django REST Framework + SimpleJWT
> **Frontend**: React.js
> **Database**: PostgreSQL

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Firebase Project Setup (Console)](#2-firebase-project-setup-console)
3. [Backend Setup (Django)](#3-backend-setup-django)
4. [Frontend Setup (React.js)](#4-frontend-setup-reactjs)
5. [Multi-Device Login Handling](#5-multi-device-login-handling)
6. [Notification Data Structure & Deep Linking](#6-notification-data-structure--deep-linking)
7. [Step-by-Step Implementation Sequence](#7-step-by-step-implementation-sequence)
8. [Testing Guide](#8-testing-guide)
9. [Production Considerations](#9-production-considerations)

---

## 1. Architecture Overview

### System Flow

```
User Login (React.js)
    |
    v
JWT Auth Success ──> Request Browser Notification Permission
    |                           |
    v                           v
Store JWT tokens        FCM getToken(messaging, {vapidKey})
                                |
                                v
                        POST /api/v1/notifications/devices/register/
                                |
                                v
                        UserDevice(user, fcm_token) saved in PostgreSQL

─── When an Event Happens ───

Backend Event (e.g., Gate Entry Created, GRPO Posted)
    |
    v
Django Signal (post_save)
    |
    v
NotificationService.send_notification_to_user()
    |
    ├──> Create Notification record in DB (for in-app notification center)
    |
    └──> Fetch all active UserDevice tokens for the recipient
         |
         v
    firebase_admin.messaging.send() for each token
         |
         v
    FCM Server ──> Push to Browser
         |
         v
    Service Worker (background) OR onMessage callback (foreground)
         |
         v
    User Clicks Notification ──> Navigate to click_action_url
```

### Tech Stack

| Layer     | Technology                  | Purpose                              |
|-----------|-----------------------------|--------------------------------------|
| Backend   | `firebase-admin` (Python)   | Send FCM push notifications          |
| Backend   | Django Signals              | Auto-trigger notifications on events |
| Backend   | Django REST Framework       | Notification APIs                    |
| Frontend  | `firebase` (JS SDK)         | Receive push notifications           |
| Frontend  | Service Worker              | Handle background notifications      |
| Database  | PostgreSQL                  | Store devices, notifications         |

---

## 2. Firebase Project Setup (Console)

### Step 2.1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"**
3. Enter project name: `sampurn-factory-app`
4. Enable/disable Google Analytics (optional)
5. Click **"Create project"**

### Step 2.2: Add a Web App

1. In your Firebase project, click the **Web icon** (`</>`) to add a web app
2. Register app name: `sampurn-factory-web`
3. Copy the **Firebase config object** — you'll need these values:
   ```javascript
   const firebaseConfig = {
     apiKey: "AIza...",
     authDomain: "sampurn-factory-app.firebaseapp.com",
     projectId: "sampurn-factory-app",
     storageBucket: "sampurn-factory-app.appspot.com",
     messagingSenderId: "123456789",
     appId: "1:123456789:web:abc123",
   };
   ```

### Step 2.3: Enable Cloud Messaging & Get VAPID Key

1. Go to **Project Settings** > **Cloud Messaging** tab
2. Under **Web configuration**, click **"Generate key pair"**
3. Copy the **VAPID key** (public key) — this is used by the frontend to subscribe to push notifications
4. Save this key securely

### Step 2.4: Download Service Account Key (for Backend)

1. Go to **Project Settings** > **Service accounts** tab
2. Click **"Generate new private key"**
3. Download the JSON file
4. Rename it to `firebase-service-account.json`
5. Place it in the Django project root (`d:\factory_app\firebase-service-account.json`)
6. **CRITICAL**: Add this file to `.gitignore` — NEVER commit it to version control

```gitignore
# Firebase
firebase-service-account.json
```

---

## 3. Backend Setup (Django)

### 3.1: New `notifications` App

Create a new Django app:

```bash
python manage.py startapp notifications
```

### 3.2: Install Dependency

Add to `requirement.txt`:
```
firebase-admin==6.6.0
```

Install:
```bash
pip install firebase-admin==6.6.0
```

### 3.3: Update Settings

**File: `config/settings.py`**

Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ... existing apps ...
    'grpo',
    'notifications',  # <-- ADD THIS
]
```

Add Firebase config at the bottom:
```python
# Firebase Cloud Messaging
FCM_CREDENTIALS_PATH = config('FCM_CREDENTIALS_PATH', default='firebase-service-account.json')
```

### 3.4: Update Environment Variables

**File: `.env`**
```
FCM_CREDENTIALS_PATH=firebase-service-account.json
```

### 3.5: Update URLs

**File: `config/urls.py`**

Add the notifications URL:
```python
urlpatterns = [
    # ... existing urls ...
    path("api/v1/notifications/", include("notifications.urls")),
]
```

### 3.6: Models

**File: `notifications/models.py`**

Two models are needed:

#### Model 1: `UserDevice` — Stores FCM tokens per device/browser

| Field         | Type          | Description                                |
|---------------|---------------|--------------------------------------------|
| `user`        | ForeignKey    | Link to User (one user can have many devices) |
| `fcm_token`   | TextField     | FCM registration token (unique per browser) |
| `device_type` | CharField     | `WEB`, `ANDROID`, or `IOS`                  |
| `device_info` | CharField     | Browser user-agent string                   |
| `is_active`   | BooleanField  | Whether this token is still valid           |
| `created_at`  | DateTimeField | When the device was registered              |
| `last_used_at`| DateTimeField | Last time a notification was sent to this device |

```python
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class UserDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fcm_devices")
    fcm_token = models.TextField(unique=True)
    device_type = models.CharField(
        max_length=20,
        choices=[("WEB", "Web Browser"), ("ANDROID", "Android"), ("IOS", "iOS")],
        default="WEB",
    )
    device_info = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_used_at"]

    def __str__(self):
        return f"{self.user.email} - {self.device_type}"
```

#### Model 2: `Notification` — Stored notifications for in-app notification center

| Field              | Type          | Description                                        |
|--------------------|---------------|----------------------------------------------------|
| `recipient`        | ForeignKey    | User who receives the notification                 |
| `company`          | ForeignKey    | Company context (nullable for global notifications)|
| `title`            | CharField     | Notification title                                 |
| `body`             | TextField     | Notification body text                             |
| `notification_type`| CharField     | Category (see NotificationType choices below)      |
| `click_action_url` | CharField     | Frontend route to navigate to on click             |
| `reference_type`   | CharField     | Entity type: `vehicle_entry`, `inspection`, etc.   |
| `reference_id`     | IntegerField  | ID of the referenced entity                        |
| `is_read`          | BooleanField  | Whether the user has read this notification        |
| `read_at`          | DateTimeField | When the notification was read                     |
| `extra_data`       | JSONField     | Additional JSON payload                            |
| `created_at`       | DateTimeField | When the notification was created                  |
| `created_by`       | ForeignKey    | User who triggered/sent the notification           |

**Notification Types:**

```python
class NotificationType(models.TextChoices):
    GATE_ENTRY_CREATED = "GATE_ENTRY_CREATED", "Gate Entry Created"
    GATE_ENTRY_STATUS_CHANGED = "GATE_ENTRY_STATUS_CHANGED", "Gate Entry Status Changed"
    SECURITY_CHECK_DONE = "SECURITY_CHECK_DONE", "Security Check Completed"
    WEIGHMENT_RECORDED = "WEIGHMENT_RECORDED", "Weighment Recorded"
    ARRIVAL_SLIP_SUBMITTED = "ARRIVAL_SLIP_SUBMITTED", "Arrival Slip Submitted"
    QC_INSPECTION_SUBMITTED = "QC_INSPECTION_SUBMITTED", "QC Inspection Submitted"
    QC_CHEMIST_APPROVED = "QC_CHEMIST_APPROVED", "QC Chemist Approved"
    QC_QAM_APPROVED = "QC_QAM_APPROVED", "QC QAM Approved"
    QC_REJECTED = "QC_REJECTED", "QC Rejected"
    QC_COMPLETED = "QC_COMPLETED", "QC Completed"
    GRPO_POSTED = "GRPO_POSTED", "GRPO Posted to SAP"
    GRPO_FAILED = "GRPO_FAILED", "GRPO Posting Failed"
    GENERAL_ANNOUNCEMENT = "GENERAL_ANNOUNCEMENT", "General Announcement"
```

```python
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    company = models.ForeignKey(
        "company.Company", on_delete=models.CASCADE, null=True, blank=True, related_name="notifications"
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    notification_type = models.CharField(
        max_length=50, choices=NotificationType.choices, default=NotificationType.GENERAL_ANNOUNCEMENT
    )
    click_action_url = models.CharField(max_length=500, blank=True)
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="notifications_sent"
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "-created_at"]),
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["notification_type"]),
        ]
        permissions = [
            ("can_send_notification", "Can send manual notifications"),
            ("can_send_bulk_notification", "Can send bulk/broadcast notifications"),
        ]

    def __str__(self):
        return f"{self.title} -> {self.recipient.email}"
```

### 3.7: Service Layer

**File: `notifications/services.py`**

The service layer handles all notification logic. Key methods:

| Method                       | Purpose                                              |
|------------------------------|------------------------------------------------------|
| `register_device()`         | Save/update FCM token for a user's device            |
| `unregister_device()`       | Remove FCM token on logout                           |
| `cleanup_stale_tokens()`    | Remove tokens not used in N days                     |
| `send_notification_to_user()` | Send push + create DB record for one user          |
| `send_notification_to_group()` | Send to a list of users                           |
| `send_bulk_notification()`  | Send to all users in a company (optionally by role)  |

**Firebase Admin SDK Initialization:**
```python
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

_firebase_app = None

def get_firebase_app():
    global _firebase_app
    if _firebase_app is None:
        cred = credentials.Certificate(settings.FCM_CREDENTIALS_PATH)
        _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app
```

**Key implementation details:**
- Firebase Admin SDK is initialized lazily (singleton pattern)
- On `UnregisteredError` from FCM, the stale token is auto-deactivated
- `send_notification_to_user()` creates a DB record AND sends FCM push in a single transaction
- Each user's active device tokens are fetched and notified individually

**Multi-device sending flow:**
```python
# 1. Create the in-app notification record
notification = Notification.objects.create(
    recipient=user,
    title=title,
    body=body,
    notification_type=notification_type,
    click_action_url=click_action_url,
    ...
)

# 2. Get all active FCM tokens for this user
tokens = UserDevice.objects.filter(user=user, is_active=True).values_list("fcm_token", flat=True)

# 3. Send FCM push to each token
for token in tokens:
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        data={
            "notification_id": str(notification.id),
            "notification_type": notification_type,
            "click_action_url": click_action_url,
        },
        token=token,
        webpush=messaging.WebpushConfig(
            fcm_options=messaging.WebpushFCMOptions(link=click_action_url),
            notification=messaging.WebpushNotification(
                title=title, body=body, icon="/icons/notification-icon.png"
            ),
        ),
    )
    messaging.send(message)
```

### 3.8: API Endpoints

**File: `notifications/urls.py`**

| Method | Endpoint                                        | Description                     | Auth Required |
|--------|------------------------------------------------|---------------------------------|---------------|
| POST   | `/api/v1/notifications/devices/register/`      | Register FCM device token       | Yes           |
| POST   | `/api/v1/notifications/devices/unregister/`    | Unregister FCM token (logout)   | Yes           |
| GET    | `/api/v1/notifications/`                        | List user's notifications       | Yes           |
| POST   | `/api/v1/notifications/mark-read/`             | Mark notifications as read      | Yes           |
| GET    | `/api/v1/notifications/unread-count/`          | Get unread count                | Yes           |
| POST   | `/api/v1/notifications/send/`                  | Admin: send manual notification | Yes + Permission |

**Serializers needed:**

| Serializer                     | Purpose                                    |
|--------------------------------|--------------------------------------------|
| `DeviceRegistrationSerializer` | Validate `fcm_token`, `device_type`        |
| `DeviceUnregisterSerializer`   | Validate `fcm_token`                       |
| `NotificationSerializer`       | Serialize notification for list response   |
| `NotificationMarkReadSerializer` | Validate `notification_ids` list        |
| `SendNotificationSerializer`   | Validate admin send payload                |

**Permissions (following existing pattern from `grpo/permissions.py`):**

```python
class CanSendNotification(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("notifications.can_send_notification")
```

### 3.9: Django Signals (Auto-Triggers)

**File: `notifications/signals.py`**

Signals connect to `post_save` of existing models to auto-trigger notifications:

| Signal Source Model                      | Notification Type              | When Triggered                     |
|------------------------------------------|--------------------------------|------------------------------------|
| `driver_management.VehicleEntry`         | `GATE_ENTRY_CREATED`           | New gate entry created             |
| `weighment.Weighment`                    | `WEIGHMENT_RECORDED`           | Weighment recorded                 |
| `quality_control.MaterialArrivalSlip`    | `ARRIVAL_SLIP_SUBMITTED`       | Arrival slip submitted for QC      |
| `quality_control.RawMaterialInspection`  | `QC_INSPECTION_SUBMITTED`      | Inspection submitted               |
| `quality_control.RawMaterialInspection`  | `QC_CHEMIST_APPROVED`          | QA Chemist approved                |
| `quality_control.RawMaterialInspection`  | `QC_QAM_APPROVED`              | QAM approved                       |
| `grpo.GRPOPosting`                       | `GRPO_POSTED` / `GRPO_FAILED`  | GRPO posted or failed              |

**Register signals in `notifications/apps.py`:**
```python
class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        import notifications.signals  # noqa: F401
```

**Recipient logic:** Notify all active users in the same company, excluding the user who triggered the event.

### 3.10: Admin Panel

**File: `notifications/admin.py`**

Register both models in Django admin for monitoring:
- `UserDeviceAdmin` — view registered devices, filter by type/active status
- `NotificationAdmin` — view all notifications, filter by type/read status

### 3.11: Management Command

**File: `notifications/management/commands/cleanup_stale_fcm_tokens.py`**

```bash
python manage.py cleanup_stale_fcm_tokens --days 30
```

Removes device tokens that haven't been used in 30 days. Schedule this as a cron job in production.

### 3.12: Data Migration for Permission Groups

Create a data migration (following the pattern from `grpo/migrations/0003_create_grpo_group.py`) to create a "Notification Sender" group with `can_send_notification` and `can_send_bulk_notification` permissions.

---

## 4. Frontend Setup (React.js)

### 4.1: Install Firebase SDK

```bash
npm install firebase
```

### 4.2: Firebase Configuration

**File: `src/config/firebase.js`**

```javascript
import { initializeApp } from "firebase/app";
import { getMessaging, getToken, onMessage } from "firebase/messaging";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

export { messaging, getToken, onMessage };
```

**File: `.env` (frontend root)**
```
VITE_FIREBASE_API_KEY=your_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
VITE_FIREBASE_VAPID_KEY=your_vapid_key
```

### 4.3: Service Worker (Background Notifications)

**File: `public/firebase-messaging-sw.js`**

> This file MUST be in `public/` so it's served at the root domain (`/firebase-messaging-sw.js`). FCM requires this.

```javascript
importScripts("https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "your_key",
  authDomain: "your_project.firebaseapp.com",
  projectId: "your_project_id",
  storageBucket: "your_project.appspot.com",
  messagingSenderId: "your_sender_id",
  appId: "your_app_id",
});

const messaging = firebase.messaging();

// Handle background messages (when app is not in focus)
messaging.onBackgroundMessage((payload) => {
  const { title, body } = payload.notification || {};
  const clickActionUrl = payload.data?.click_action_url || "/";

  self.registration.showNotification(title || "Factory App", {
    body: body || "",
    icon: "/icons/notification-icon.png",
    data: { click_action_url: clickActionUrl },
  });
});

// Handle notification click -> navigate to specific page
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = event.notification.data?.click_action_url || "/";

  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((clientList) => {
      // If app is already open, focus it and navigate
      for (const client of clientList) {
        if ("focus" in client) {
          client.focus();
          client.postMessage({ type: "NOTIFICATION_CLICK", url });
          return;
        }
      }
      // Otherwise open the app in a new window
      return clients.openWindow(url);
    })
  );
});
```

### 4.4: FCM Token Manager Hook

**File: `src/hooks/useFCM.js`**

This hook manages the full FCM lifecycle:

```javascript
import { useEffect, useRef, useCallback } from "react";
import { messaging, getToken, onMessage } from "../config/firebase";
import api from "../services/api"; // your axios instance

const VAPID_KEY = import.meta.env.VITE_FIREBASE_VAPID_KEY;

export function useFCM({ onForegroundMessage } = {}) {
  const tokenRef = useRef(null);

  // Register FCM token with backend
  const registerToken = useCallback(async (token) => {
    try {
      await api.post("/api/v1/notifications/devices/register/", {
        fcm_token: token,
        device_type: "WEB",
        device_info: navigator.userAgent.substring(0, 255),
      });
      tokenRef.current = token;
    } catch (err) {
      console.error("Failed to register FCM token:", err);
    }
  }, []);

  // Unregister FCM token from backend (call on logout)
  const unregisterToken = useCallback(async () => {
    if (tokenRef.current) {
      try {
        await api.post("/api/v1/notifications/devices/unregister/", {
          fcm_token: tokenRef.current,
        });
        tokenRef.current = null;
      } catch (err) {
        console.error("Failed to unregister FCM token:", err);
      }
    }
  }, []);

  // Request permission and get FCM token
  const requestPermissionAndGetToken = useCallback(async () => {
    try {
      const permission = await Notification.requestPermission();
      if (permission === "granted") {
        const token = await getToken(messaging, { vapidKey: VAPID_KEY });
        if (token) await registerToken(token);
      }
    } catch (err) {
      console.error("FCM permission/token error:", err);
    }
  }, [registerToken]);

  // Listen for foreground messages
  useEffect(() => {
    const unsubscribe = onMessage(messaging, (payload) => {
      if (onForegroundMessage) onForegroundMessage(payload);
    });
    return () => unsubscribe();
  }, [onForegroundMessage]);

  // Listen for service worker notification clicks
  useEffect(() => {
    const handler = (event) => {
      if (event.data?.type === "NOTIFICATION_CLICK") {
        // Navigate using your router (React Router, etc.)
        window.location.href = event.data.url;
      }
    };
    navigator.serviceWorker?.addEventListener("message", handler);
    return () => navigator.serviceWorker?.removeEventListener("message", handler);
  }, []);

  return { unregisterToken, requestPermissionAndGetToken };
}
```

**Usage Flow:**
1. After login success → call `requestPermissionAndGetToken()`
2. Browser asks user for notification permission
3. If granted → FCM token is sent to backend → stored in `UserDevice`
4. On logout → call `unregisterToken()` → token removed from backend

### 4.5: Notification Bell Component

**File: `src/components/NotificationBell.jsx`**

Features:
- Bell icon with unread count badge
- Dropdown showing recent notifications
- "Mark all as read" button
- Click on notification → navigate to the relevant page
- Polls unread count every 30 seconds

```
┌──────────────────────────────┐
│  🔔 (3)                      │ <-- Bell icon with badge
├──────────────────────────────┤
│  Notifications    Mark all   │
├──────────────────────────────┤
│  ● Gate Entry Created        │ <-- Unread (bold)
│    Entry RM-2025-001 created │
│    2 min ago                 │
├──────────────────────────────┤
│    Weighment Recorded        │ <-- Read (normal)
│    Net weight: 2500 kg       │
│    15 min ago                │
├──────────────────────────────┤
│    GRPO Posted               │
│    SAP Doc: 50000123         │
│    1 hour ago                │
└──────────────────────────────┘
```

### 4.6: Integration Points

**Login flow:**
```
User submits email/password
    → POST /api/v1/accounts/login/
    → Receive JWT tokens
    → Store tokens
    → useFCM hook auto-triggers requestPermissionAndGetToken()
    → FCM token registered with backend
```

**Logout flow:**
```
User clicks logout
    → Call unregisterToken() (removes FCM token from backend)
    → Clear JWT tokens
    → Redirect to login page
```

**Foreground notification (app is open):**
```
FCM message arrives
    → onMessage callback fires
    → Show toast/snackbar notification in-app
    → Update unread count badge
```

**Background notification (app is not focused):**
```
FCM message arrives
    → Service worker handles it
    → Browser shows native push notification
    → User clicks notification
    → Service worker opens app / focuses existing tab
    → Navigates to click_action_url
```

---

## 5. Multi-Device Login Handling

### The Problem
One user may login from multiple browsers/devices (office desktop, laptop, phone browser). Each device needs to receive notifications independently.

### The Solution

**One user → many FCM tokens** via the `UserDevice` model:

```
User: john@example.com
    ├── Device 1: Chrome on Desktop    → fcm_token_abc123 (active)
    ├── Device 2: Firefox on Laptop    → fcm_token_def456 (active)
    └── Device 3: Safari on iPhone     → fcm_token_ghi789 (active)
```

### How It Works

| Scenario                      | Action                                                        |
|-------------------------------|---------------------------------------------------------------|
| User logs in on Device A      | Register Device A's FCM token → stored in `UserDevice`        |
| User logs in on Device B      | Register Device B's FCM token → new `UserDevice` record       |
| Notification sent to user     | Fetch ALL active tokens → send FCM push to each one           |
| User logs out from Device A   | Unregister Device A's token → removed from `UserDevice`       |
| Device B still gets notifs    | Yes, Device B's token is still active                         |
| Same browser, different user  | Old token reassigned to new user (old user stops getting notifs) |
| Browser refreshes FCM token   | On next login, new token is registered, old one gets cleaned up |
| Token expires (stale)         | `cleanup_stale_fcm_tokens` command removes tokens unused for 30+ days |
| FCM returns `UnregisteredError` | Token auto-deactivated (set `is_active=False`)              |

### Token Lifecycle

```
                Register
                   |
                   v
    [FCM Token Created] ──> Active in UserDevice
          |                        |
          |  (on logout)           |  (FCM sends UnregisteredError)
          v                        v
    [Token Deleted]          [Token Deactivated]
                                   |
                                   v
                            [Cleanup Command Deletes]
```

---

## 6. Notification Data Structure & Deep Linking

### FCM Payload Structure

Every notification sent via FCM contains:

```json
{
  "notification": {
    "title": "Gate Entry Created",
    "body": "Entry RM-2025-001 for raw material has been created"
  },
  "data": {
    "notification_id": "42",
    "notification_type": "GATE_ENTRY_CREATED",
    "click_action_url": "/gate-entries/123",
    "reference_type": "vehicle_entry",
    "reference_id": "123"
  },
  "webpush": {
    "fcm_options": {
      "link": "/gate-entries/123"
    }
  }
}
```

### Deep Linking URL Map

| Notification Type              | `click_action_url` Pattern            | Description                       |
|--------------------------------|---------------------------------------|-----------------------------------|
| `GATE_ENTRY_CREATED`          | `/gate-entries/{entry_id}`            | Go to gate entry detail page      |
| `GATE_ENTRY_STATUS_CHANGED`   | `/gate-entries/{entry_id}`            | Go to gate entry detail page      |
| `SECURITY_CHECK_DONE`         | `/gate-entries/{entry_id}`            | Go to gate entry detail page      |
| `WEIGHMENT_RECORDED`          | `/gate-entries/{entry_id}`            | Go to gate entry with weighment   |
| `ARRIVAL_SLIP_SUBMITTED`      | `/gate-entries/{entry_id}/qc`         | Go to QC section of gate entry    |
| `QC_INSPECTION_SUBMITTED`     | `/gate-entries/{entry_id}/qc/{insp_id}` | Go to specific inspection       |
| `QC_CHEMIST_APPROVED`         | `/gate-entries/{entry_id}/qc/{insp_id}` | Go to specific inspection       |
| `QC_QAM_APPROVED`             | `/gate-entries/{entry_id}/qc/{insp_id}` | Go to specific inspection       |
| `QC_REJECTED`                 | `/gate-entries/{entry_id}/qc/{insp_id}` | Go to specific inspection       |
| `QC_COMPLETED`                | `/gate-entries/{entry_id}/qc/{insp_id}` | Go to specific inspection       |
| `GRPO_POSTED`                 | `/grpo/{grpo_id}`                     | Go to GRPO detail page            |
| `GRPO_FAILED`                 | `/grpo/{grpo_id}`                     | Go to GRPO detail page            |
| `GENERAL_ANNOUNCEMENT`        | `/notifications`                      | Go to notification center         |

> **Note:** Adjust the URL patterns to match your actual React Router routes.

### Click Handling Flow

```
User clicks browser push notification
    |
    v
Service Worker catches "notificationclick" event
    |
    v
Extract click_action_url from notification.data
    |
    ├── App is already open?
    |       |
    |       YES → Focus existing tab → postMessage({type: "NOTIFICATION_CLICK", url})
    |                                     |
    |                                     v
    |                               React app receives message → navigate(url)
    |
    └── App is NOT open?
            |
            v
        clients.openWindow(click_action_url) → Opens app at that route
```

---

## 7. Step-by-Step Implementation Sequence

### Step 1: Firebase Console Setup
- [ ] Create Firebase project
- [ ] Add web app, copy config
- [ ] Generate VAPID key
- [ ] Download service account JSON
- [ ] Add `firebase-service-account.json` to `.gitignore`

### Step 2: Backend — Install & Configure
- [ ] `pip install firebase-admin==6.6.0`
- [ ] Add to `requirement.txt`
- [ ] Add `FCM_CREDENTIALS_PATH` to `.env`
- [ ] Add Firebase settings to `config/settings.py`
- [ ] Place `firebase-service-account.json` in project root

### Step 3: Backend — Create Notifications App
- [ ] `python manage.py startapp notifications`
- [ ] Add `'notifications'` to `INSTALLED_APPS`
- [ ] Add URL route in `config/urls.py`

### Step 4: Backend — Models & Migrate
- [ ] Create `UserDevice` and `Notification` models
- [ ] Define `NotificationType` choices
- [ ] Run `python manage.py makemigrations notifications`
- [ ] Run `python manage.py migrate`

### Step 5: Backend — Service Layer
- [ ] Create `notifications/services.py`
- [ ] Implement Firebase Admin SDK initialization
- [ ] Implement `register_device()`, `unregister_device()`
- [ ] Implement `send_notification_to_user()`, `send_notification_to_group()`, `send_bulk_notification()`
- [ ] Test FCM sending manually via Django shell

### Step 6: Backend — APIs
- [ ] Create serializers (`notifications/serializers.py`)
- [ ] Create views (`notifications/views.py`)
- [ ] Create URLs (`notifications/urls.py`)
- [ ] Create permissions (`notifications/permissions.py`)
- [ ] Register admin (`notifications/admin.py`)

### Step 7: Backend — Signals & Auto-Triggers
- [ ] Create `notifications/signals.py` with `post_save` receivers
- [ ] Register signals in `notifications/apps.py` `ready()` method
- [ ] Test: create a gate entry → verify notification is created in DB

### Step 8: Backend — Migrations & Management
- [ ] Create data migration for "Notification Sender" permission group
- [ ] Create `cleanup_stale_fcm_tokens` management command

### Step 9: Frontend — Firebase Integration
- [ ] `npm install firebase`
- [ ] Create `src/config/firebase.js`
- [ ] Add Firebase env variables to `.env`
- [ ] Create `public/firebase-messaging-sw.js`
- [ ] Create `src/hooks/useFCM.js`

### Step 10: Frontend — UI Components & Integration
- [ ] Create `NotificationBell` component
- [ ] Integrate `useFCM` hook into app layout
- [ ] Connect `unregisterToken()` to logout flow
- [ ] Handle notification click navigation
- [ ] Test end-to-end flow

---

## 8. Testing Guide

### 8.1: Backend API Testing

**Test device registration:**
```bash
# Login first to get JWT token
curl -X POST http://localhost:8000/api/v1/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "pass"}'

# Register device token
curl -X POST http://localhost:8000/api/v1/notifications/devices/register/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"fcm_token": "test_token_123", "device_type": "WEB"}'
```

**Test notification sending (admin):**
```bash
curl -X POST http://localhost:8000/api/v1/notifications/send/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Company-Code: JIVO_OIL" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Notification",
    "body": "This is a test notification",
    "notification_type": "GENERAL_ANNOUNCEMENT",
    "click_action_url": "/dashboard"
  }'
```

**Test notification listing:**
```bash
curl http://localhost:8000/api/v1/notifications/ \
  -H "Authorization: Bearer <access_token>"
```

### 8.2: End-to-End Test

1. **Login** on the React app in Chrome
2. **Allow** notification permission when prompted
3. Verify: `UserDevice` record created in Django admin with the FCM token
4. **Trigger an event**: create a gate entry via the app or API
5. Verify: `Notification` record created in DB
6. Verify: **Push notification** appears in Chrome
7. **Click** the notification
8. Verify: App navigates to the correct page (e.g., gate entry detail)
9. **Check notification bell**: unread count decremented, notification marked as read
10. **Login on another browser** (Firefox), repeat steps 4-9
11. Verify: BOTH browsers receive the notification
12. **Logout from Chrome**
13. Verify: Chrome's FCM token removed from `UserDevice`
14. Trigger another event
15. Verify: Only Firefox receives the notification (Chrome does NOT)

### 8.3: Django Shell Testing

```python
from notifications.services import NotificationService
from accounts.models import User

user = User.objects.get(email="admin@example.com")

# Test sending
NotificationService.send_notification_to_user(
    user=user,
    title="Shell Test",
    body="Testing from Django shell",
    click_action_url="/dashboard",
)
```

---

## 9. Production Considerations

### 9.1: Performance — Async Notification Sending

Signals run synchronously in the request cycle. For production with many users, wrap notification sending in a background task using **Celery** or **Django-Q**:

```python
# Instead of directly calling in signal:
NotificationService.send_notification_to_user(...)

# Wrap in Celery task:
@shared_task
def send_notification_task(user_id, title, body, ...):
    user = User.objects.get(id=user_id)
    NotificationService.send_notification_to_user(user=user, ...)
```

### 9.2: Stale Token Cleanup (Cron Job)

Schedule the management command to run daily:

```bash
# Crontab entry
0 2 * * * cd /path/to/factory_app && python manage.py cleanup_stale_fcm_tokens --days 30
```

### 9.3: HTTPS Requirement

FCM push notifications require HTTPS in production. Development on `localhost` works without HTTPS.

### 9.4: Notification Icon

Place a notification icon at `public/icons/notification-icon.png` (192x192 px recommended) for the browser push notification display.

### 9.5: Rate Limiting

Consider adding rate limiting to the notification send API to prevent abuse:
- Max 100 manual notifications per admin per hour
- Max 1000 bulk notifications per day per company

### 9.6: Notification Retention

Consider adding a periodic cleanup for old notifications:
```bash
python manage.py cleanup_old_notifications --days 90
```

---

## Files Summary

### New Files to Create

| File                                                          | Purpose                          |
|---------------------------------------------------------------|----------------------------------|
| `notifications/__init__.py`                                    | App init                         |
| `notifications/apps.py`                                        | AppConfig with signal registration |
| `notifications/models.py`                                      | UserDevice + Notification models |
| `notifications/services.py`                                    | NotificationService (FCM + DB)   |
| `notifications/serializers.py`                                 | DRF serializers                  |
| `notifications/views.py`                                       | API views                        |
| `notifications/urls.py`                                        | URL routing                      |
| `notifications/permissions.py`                                 | Custom permissions               |
| `notifications/admin.py`                                       | Admin panel registration         |
| `notifications/signals.py`                                     | Auto-trigger signals             |
| `notifications/management/commands/cleanup_stale_fcm_tokens.py` | Stale token cleanup            |
| `notifications/migrations/0002_create_notification_groups.py`   | Permission group migration      |
| `firebase-service-account.json`                                | Firebase credentials (DO NOT COMMIT) |

### Existing Files to Modify

| File                  | Change                                         |
|-----------------------|------------------------------------------------|
| `config/settings.py`  | Add `'notifications'` to INSTALLED_APPS + FCM config |
| `config/urls.py`      | Add notifications URL route                    |
| `requirement.txt`     | Add `firebase-admin==6.6.0`                    |
| `.env`                | Add `FCM_CREDENTIALS_PATH`                     |
| `.gitignore`          | Add `firebase-service-account.json`            |

### Frontend Files (React.js project)

| File                                    | Purpose                           |
|-----------------------------------------|-----------------------------------|
| `src/config/firebase.js`               | Firebase SDK initialization        |
| `public/firebase-messaging-sw.js`       | Service worker for background push |
| `src/hooks/useFCM.js`                  | FCM token lifecycle hook           |
| `src/components/NotificationBell.jsx`   | Notification bell UI component     |
