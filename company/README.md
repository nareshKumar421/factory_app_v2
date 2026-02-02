# Company Module

## Overview

The **Company Module** manages multi-company support, user-company relationships, and role-based access control. It enables users to belong to multiple companies with different roles.

---

## Models

### Company

| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField(200) | Company name |
| `code` | CharField(50) | Unique company code (e.g., JIVO_OIL) |
| `is_active` | BooleanField | Active status (default: True) |

### UserRole

| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField(100) | Role name (Admin, QC, Store, etc.) |
| `description` | TextField | Role description |

### UserCompany

| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey | Link to User |
| `company` | ForeignKey | Link to Company |
| `role` | ForeignKey | Link to UserRole |
| `is_default` | BooleanField | Default company for user |
| `is_active` | BooleanField | Active status |

**Constraints:** Unique together (user, company)

---

## API Documentation

### Base URL
```
/api/v1/company/
```

### Headers Required
```
Authorization: Bearer <access_token>
Company-Code: <company_code>
```

---

### 1. List Companies

```
GET /api/v1/company/companies/
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "JIVO OIL",
        "code": "JIVO_OIL",
        "is_active": true
    },
    {
        "id": 2,
        "name": "JIVO MART",
        "code": "JIVO_MART",
        "is_active": true
    }
]
```

---

### 2. Get Company Details

```
GET /api/v1/company/companies/{id}/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "JIVO OIL",
    "code": "JIVO_OIL",
    "is_active": true
}
```

---

### 3. Create Company

```
POST /api/v1/company/companies/
```

**Request Body:**
```json
{
    "name": "New Company",
    "code": "NEW_COMP",
    "is_active": true
}
```

**Response (201 Created):**
```json
{
    "id": 3,
    "name": "New Company",
    "code": "NEW_COMP",
    "is_active": true
}
```

---

### 4. Update Company

```
PUT /api/v1/company/companies/{id}/
```

**Request Body:**
```json
{
    "name": "Updated Company Name",
    "code": "NEW_COMP",
    "is_active": true
}
```

**Response (200 OK):**
```json
{
    "id": 3,
    "name": "Updated Company Name",
    "code": "NEW_COMP",
    "is_active": true
}
```

---

### 5. Delete Company

```
DELETE /api/v1/company/companies/{id}/
```

**Response (204 No Content)**

---

## Company Context Permission

The `HasCompanyContext` permission class validates the `Company-Code` header and attaches the company context to the request.

**Usage in Views:**
```python
from company.permissions import HasCompanyContext

class MyView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyContext]

    def get(self, request):
        company = request.company.company  # Access company from request
```

---

## Multi-Company Flow

```
┌──────────────┐
│    Login     │──────► User receives list of assigned companies
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Select     │──────► User selects company to work with
│   Company    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  API Calls   │──────► Include Company-Code header in all requests
│              │        Company-Code: JIVO_OIL
└──────────────┘
```

---

## Module Structure

```
company/
├── __init__.py
├── apps.py
├── models.py           # Company, UserRole, UserCompany
├── serializers.py      # CompanySerializer
├── views.py            # CompanyViewSet
├── urls.py             # Router configuration
├── permissions.py      # HasCompanyContext
├── admin.py            # Admin configuration
└── migrations/
```
