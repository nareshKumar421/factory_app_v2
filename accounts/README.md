# Accounts Module

## Overview

The **Accounts Module** handles user authentication, authorization, and department management. It provides a custom user model with email-based authentication and JWT token management.

---

## Models

### User (Custom User Model)

| Field | Type | Description |
|-------|------|-------------|
| `email` | EmailField | Unique, primary identifier for authentication |
| `full_name` | CharField(150) | User's full name |
| `employee_code` | CharField(50) | Unique employee identifier |
| `is_active` | BooleanField | Account active status (default: True) |
| `is_staff` | BooleanField | Staff privileges (default: False) |
| `date_joined` | DateTimeField | Account creation timestamp |

### Department

| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField(100) | Department name |
| `description` | TextField | Optional description |

---

## API Documentation

### Base URL
```
/api/v1/accounts/
```

---

### 1. Login

```
POST /api/v1/accounts/login/
```

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "your_password"
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token": {
        "access_expires_in": 90000,
        "refresh_expires_in": 604800
    },
    "user": {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe",
        "companies": [
            {
                "company_id": 1,
                "company_name": "JIVO OIL",
                "company_code": "JIVO_OIL",
                "role": "Admin",
                "is_default": true
            }
        ]
    }
}
```

**Error Response (401):**
```json
{
    "detail": "No active account found with the given credentials"
}
```

---

### 2. Refresh Token

```
POST /api/v1/accounts/token/refresh/
```

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token": {
        "access_expires_in": 90000,
        "refresh_expires_in": 604800
    }
}
```

---

### 3. Get Current User (Me)

```
GET /api/v1/accounts/me/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "employee_code": "EMP001",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2026-01-01T10:00:00Z",
    "companies": [
        {
            "company_id": 1,
            "company_name": "JIVO OIL",
            "company_code": "JIVO_OIL",
            "role": "Admin",
            "is_default": true,
            "is_active": true
        }
    ],
    "permissions": [
        "accounts.add_user",
        "accounts.change_user",
        "accounts.view_user"
    ]
}
```

---

### 4. Change Password

```
POST /api/v1/accounts/change-password/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "old_password": "current_password",
    "new_password": "new_secure_password"
}
```

**Response (200 OK):**
```json
{
    "message": "Password changed successfully"
}
```

**Error Response (400):**
```json
{
    "detail": "Old password is incorrect"
}
```

---

### 5. List Departments

```
GET /api/v1/accounts/departments/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Quality Control",
        "description": "Handles product quality inspection"
    },
    {
        "id": 2,
        "name": "Store",
        "description": "Warehouse and inventory management"
    }
]
```

---

## Authentication Flow

```
┌──────────────┐
│   Login      │──────► POST /login/ with email & password
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Get Tokens  │──────► Receive access & refresh tokens
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Use Access  │──────► Include in Authorization header
│    Token     │        Bearer <access_token>
└──────┬───────┘
       │
       ▼
┌──────────────┐
│Token Expired?│──────► POST /token/refresh/ with refresh token
└──────────────┘
```

---

## Module Structure

```
accounts/
├── __init__.py
├── apps.py
├── models.py           # User, Department models
├── managers.py         # Custom UserManager
├── serializers.py      # Login, Me, ChangePassword serializers
├── views.py            # API views
├── urls.py             # URL routing
├── admin.py            # Admin configuration
└── migrations/
```
