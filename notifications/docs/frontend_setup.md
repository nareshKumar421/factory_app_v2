# Notifications - Frontend Setup Guide (React.js)

Step-by-step guide for integrating Firebase Cloud Messaging in the React.js frontend.

---

## 1. Install Firebase SDK

```bash
npm install firebase
```

---

## 2. Firebase Configuration

Create `src/config/firebase.js`:

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

Add to `.env` (frontend root):

```
VITE_FIREBASE_API_KEY=your_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
VITE_FIREBASE_VAPID_KEY=your_vapid_key
```

---

## 3. Service Worker (Background Notifications)

Create `public/firebase-messaging-sw.js`:

> This file MUST be in `public/` so it's served at `/firebase-messaging-sw.js`. FCM requires root scope.

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

// Handle background messages (app not in focus)
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
      for (const client of clientList) {
        if ("focus" in client) {
          client.focus();
          client.postMessage({ type: "NOTIFICATION_CLICK", url });
          return;
        }
      }
      return clients.openWindow(url);
    })
  );
});
```

---

## 4. FCM Token Manager Hook

Create `src/hooks/useFCM.js`:

```javascript
import { useEffect, useRef, useCallback } from "react";
import { messaging, getToken, onMessage } from "../config/firebase";
import api from "../services/api"; // your axios instance

const VAPID_KEY = import.meta.env.VITE_FIREBASE_VAPID_KEY;

export function useFCM({ onForegroundMessage } = {}) {
  const tokenRef = useRef(null);

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
        window.location.href = event.data.url;
        // Or use your React Router: navigate(event.data.url)
      }
    };
    navigator.serviceWorker?.addEventListener("message", handler);
    return () => navigator.serviceWorker?.removeEventListener("message", handler);
  }, []);

  return { unregisterToken, requestPermissionAndGetToken };
}
```

---

## 5. Integration into App Layout

In your main layout component:

```javascript
import { useFCM } from "../hooks/useFCM";
import { toast } from "your-toast-library";

export default function AppLayout({ children }) {
  const { unregisterToken, requestPermissionAndGetToken } = useFCM({
    onForegroundMessage: (payload) => {
      toast.info(payload.notification?.title || "New notification");
      // Optionally refresh notification bell count here
    },
  });

  // Call on login success
  useEffect(() => {
    if (isAuthenticated) {
      requestPermissionAndGetToken();
    }
  }, [isAuthenticated]);

  const handleLogout = async () => {
    await unregisterToken();
    // ... existing logout logic
  };

  return (
    <div>
      <header>
        <NotificationBell />
        <button onClick={handleLogout}>Logout</button>
      </header>
      <main>{children}</main>
    </div>
  );
}
```

---

## 6. Notification Bell Component

Create `src/components/NotificationBell.jsx`:

```javascript
import { useState, useEffect, useCallback } from "react";
import api from "../services/api";

export default function NotificationBell() {
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchUnreadCount = useCallback(async () => {
    try {
      const { data } = await api.get("/api/v1/notifications/unread-count/");
      setUnreadCount(data.unread_count);
    } catch (err) {
      console.error("Failed to fetch unread count:", err);
    }
  }, []);

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get("/api/v1/notifications/", {
        params: { page: 1, page_size: 20 },
      });
      setNotifications(data.results);
      setUnreadCount(data.unread_count);
    } catch (err) {
      console.error("Failed to fetch notifications:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  const markAsRead = useCallback(async (ids = []) => {
    try {
      await api.post("/api/v1/notifications/mark-read/", {
        notification_ids: ids,
      });
      fetchUnreadCount();
      if (isOpen) fetchNotifications();
    } catch (err) {
      console.error("Failed to mark as read:", err);
    }
  }, [fetchUnreadCount, fetchNotifications, isOpen]);

  const handleNotificationClick = useCallback((notification) => {
    if (!notification.is_read) markAsRead([notification.id]);
    if (notification.click_action_url) {
      window.location.href = notification.click_action_url;
    }
    setIsOpen(false);
  }, [markAsRead]);

  // Poll unread count every 30 seconds
  useEffect(() => {
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(interval);
  }, [fetchUnreadCount]);

  // Fetch list when dropdown opens
  useEffect(() => {
    if (isOpen) fetchNotifications();
  }, [isOpen, fetchNotifications]);

  return (
    <div style={{ position: "relative" }}>
      <button onClick={() => setIsOpen(!isOpen)}>
        Bell {unreadCount > 0 && <span>({unreadCount})</span>}
      </button>

      {isOpen && (
        <div style={{
          position: "absolute", right: 0, top: "100%",
          width: 350, maxHeight: 400, overflow: "auto",
          background: "#fff", border: "1px solid #ddd", borderRadius: 8
        }}>
          <div style={{ padding: 12, display: "flex", justifyContent: "space-between" }}>
            <strong>Notifications</strong>
            {unreadCount > 0 && (
              <button onClick={() => markAsRead([])}>Mark all read</button>
            )}
          </div>

          {loading && <p style={{ padding: 12 }}>Loading...</p>}
          {!loading && notifications.length === 0 && (
            <p style={{ padding: 12 }}>No notifications</p>
          )}

          {notifications.map((n) => (
            <div
              key={n.id}
              onClick={() => handleNotificationClick(n)}
              style={{
                padding: 12, cursor: "pointer", borderTop: "1px solid #eee",
                background: n.is_read ? "#fff" : "#f0f7ff",
              }}
            >
              <strong>{n.title}</strong>
              <p style={{ margin: "4px 0", fontSize: 13, color: "#666" }}>{n.body}</p>
              <small style={{ color: "#999" }}>
                {new Date(n.created_at).toLocaleString()}
              </small>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## 7. Notification Click Flow

```
Background notification click:
  Service Worker -> notificationclick event
    -> clients.matchAll() -> find open tab
    -> postMessage({ type: "NOTIFICATION_CLICK", url })
    -> useFCM hook listener -> window.location.href = url

Foreground notification (app open):
  FCM onMessage -> onForegroundMessage callback
    -> Show toast notification
    -> User clicks toast -> navigate to click_action_url

In-app notification bell:
  User clicks notification item
    -> handleNotificationClick()
    -> Mark as read via API
    -> Navigate to click_action_url
```

---

## 8. Notification Icon

Place a 192x192 PNG icon at `public/icons/notification-icon.png` for the browser push notification display. This path is referenced in:
- `firebase-messaging-sw.js` (background notifications)
- `NotificationService._build_fcm_message()` (backend FCM payload)
