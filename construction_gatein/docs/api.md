# Construction Gate-In API Documentation

## Base URL
```
/api/v1/construction-gatein/
```

## Headers Required
```
Authorization: Bearer <access_token>
Company-Code: <company_code>
```

---

## Endpoints

### 1. Get Construction Entry

Retrieve existing construction entry for a gate entry.

```
GET /api/v1/construction-gatein/gate-entries/{gate_entry_id}/construction/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `construction_gatein.view_constructiongateentry`

**Response (200 OK):**
```json
{
    "id": 1,
    "project_name": "Factory Expansion Phase 2",
    "work_order_number": "WO-2026-001",
    "contractor_name": "ABC Construction",
    "contractor_contact": "+919876543210",
    "material_category": {
        "id": 1,
        "category_name": "Cement"
    },
    "material_description": "OPC 53 Grade Cement",
    "quantity": "500.00",
    "unit": "KG",
    "challan_number": "CH-001",
    "invoice_number": "INV-001",
    "site_engineer": "John Doe",
    "security_approval": "PENDING",
    "remarks": ""
}
```

**Error Response (404):**
```json
{
    "detail": "Construction entry does not exist"
}
```

---

### 2. Create Construction Entry

Create new construction gate entry for a vehicle entry.

```
POST /api/v1/construction-gatein/gate-entries/{gate_entry_id}/construction/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `construction_gatein.add_constructiongateentry`

**Request Body:**
```json
{
    "project_name": "Factory Expansion Phase 2",
    "contractor_name": "ABC Construction",
    "contractor_contact": "+919876543210",
    "material_category": 1,
    "material_description": "OPC 53 Grade Cement",
    "quantity": 500.00,
    "unit": "KG",
    "challan_number": "CH-001",
    "invoice_number": "INV-001",
    "site_engineer": "John Doe",
    "remarks": ""
}
```

**Response (201 Created):**
```json
{
    "message": "Construction gate entry created",
    "id": 1,
    "work_order_number": "WO-2026-001"
}
```

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Invalid entry type. Expected CONSTRUCTION.` |
| 400 | `Gate entry is locked` |
| 400 | `Construction entry already exists` |
| 403 | `You do not have permission to perform this action.` |

---

### 3. Update Construction Entry

Update existing construction gate entry.

```
PUT /api/v1/construction-gatein/gate-entries/{gate_entry_id}/construction/update/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `construction_gatein.change_constructiongateentry`

**Request Body:** (partial update supported)
```json
{
    "quantity": 600.00,
    "remarks": "Updated quantity"
}
```

**Response (200 OK):** Returns updated entry data.

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Gate entry is locked` |
| 403 | `You do not have permission to perform this action.` |
| 404 | `Construction entry does not exist` |

---

### 4. Complete Construction Entry

Complete and lock a construction gate entry.

```
POST /api/v1/construction-gatein/gate-entries/{gate_entry_id}/complete/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `construction_gatein.can_complete_construction_entry`

**Request Body:** None required

**Response (200 OK):**
```json
{
    "detail": "Construction gate entry completed successfully"
}
```

---

### 5. List Material Categories

List all active construction material categories (for dropdown).

```
GET /api/v1/construction-gatein/gate-entries/construction/categories/
```

**Permission Required:** `IsAuthenticated` + `construction_gatein.view_constructionmaterialcategory`

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "category_name": "Cement",
        "description": "All types of cement",
        "is_active": true
    },
    {
        "id": 2,
        "category_name": "Steel/Rebar",
        "description": "Steel bars and rebar",
        "is_active": true
    }
]
```

---

## Permission Summary

| Endpoint | Method | Permission Codename |
|----------|--------|---------------------|
| `/gate-entries/{id}/construction/` | GET | `view_constructiongateentry` |
| `/gate-entries/{id}/construction/` | POST | `add_constructiongateentry` |
| `/gate-entries/{id}/construction/update/` | PUT | `change_constructiongateentry` |
| `/gate-entries/{id}/complete/` | POST | `can_complete_construction_entry` |
| `/gate-entries/construction/categories/` | GET | `view_constructionmaterialcategory` |

## All Permissions

| Permission Codename | Description |
|---------------------|-------------|
| `construction_gatein.add_constructiongateentry` | Can add construction gate entry |
| `construction_gatein.view_constructiongateentry` | Can view construction gate entry |
| `construction_gatein.change_constructiongateentry` | Can change construction gate entry |
| `construction_gatein.delete_constructiongateentry` | Can delete construction gate entry |
| `construction_gatein.can_complete_construction_entry` | Can complete construction gate entry |
| `construction_gatein.view_constructionmaterialcategory` | Can view construction material category |
| `construction_gatein.can_manage_material_category` | Can manage material category |

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
