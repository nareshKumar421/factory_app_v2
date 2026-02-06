# Accounts API Documentation

## Base URL
```
/api/v1/accounts/
```

---

## Authentication Endpoints

### 1. Login

Authenticate user and get JWT tokens.

```
POST /api/v1/accounts/login/
```

**Permission Required:** None (Public)

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

Get new access token using refresh token.

```
POST /api/v1/accounts/token/refresh/
```

**Permission Required:** None (Public)

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

## User Endpoints

### 3. Get Current User (Me)

Get authenticated user's profile and permissions.

```
GET /api/v1/accounts/me/
```

**Permission Required:** `IsAuthenticated`

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
        "accounts.can_create_user",
        "accounts.can_view_user",
        "accounts.can_edit_user"
    ]
}
```

---

### 4. Change Password

Change authenticated user's password.

```
POST /api/v1/accounts/change-password/
```

**Permission Required:** `IsAuthenticated`

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

## Department Endpoints

### 5. List Departments

Get all departments.

```
GET /api/v1/accounts/departments/
```

**Permission Required:** `IsAuthenticated` + `accounts.can_view_department`

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

## Future User Management Endpoints

### 6. List Users

```
GET /api/v1/accounts/users/
```

**Permission Required:** `IsAuthenticated` + `accounts.can_view_user`

---

### 7. Create User

```
POST /api/v1/accounts/users/
```

**Permission Required:** `IsAuthenticated` + `accounts.can_create_user`

---

### 8. Get User Detail

```
GET /api/v1/accounts/users/<id>/
```

**Permission Required:** `IsAuthenticated` + `accounts.can_view_user`

**Note:** Users can always view their own profile.

---

### 9. Update User

```
PUT/PATCH /api/v1/accounts/users/<id>/
```

**Permission Required:** `IsAuthenticated` + `accounts.can_edit_user`

**Note:** Users can edit their own profile (restricted fields).

---

### 10. Delete User

```
DELETE /api/v1/accounts/users/<id>/
```

**Permission Required:** `IsAuthenticated` + `accounts.can_delete_user`

**Note:** Users cannot delete themselves.

---

### 11. Manage User Permissions

```
GET/PUT /api/v1/accounts/users/<id>/permissions/
```

**Permission Required:** `IsAuthenticated` + `accounts.can_manage_user_permissions`

---

## Permission Summary

| Endpoint | Method | Permission Required |
|----------|--------|---------------------|
| `/login/` | POST | None |
| `/token/refresh/` | POST | None |
| `/me/` | GET | IsAuthenticated |
| `/change-password/` | POST | IsAuthenticated |
| `/departments/` | GET | IsAuthenticated + can_view_department |
| `/users/` | GET | IsAuthenticated + can_view_user |
| `/users/` | POST | IsAuthenticated + can_create_user |
| `/users/<id>/` | GET | IsAuthenticated + can_view_user |
| `/users/<id>/` | PUT/PATCH | IsAuthenticated + can_edit_user |
| `/users/<id>/` | DELETE | IsAuthenticated + can_delete_user |
| `/users/<id>/permissions/` | GET/PUT | IsAuthenticated + can_manage_user_permissions |

---

## Error Responses

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```
