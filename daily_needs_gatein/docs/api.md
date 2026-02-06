# Daily Needs Gate-In API Documentation

## Base URL
```
/api/v1/daily-needs-gatein/
```

## Headers Required
```
Authorization: Bearer <access_token>
Company-Code: <company_code>
```

---

## Endpoints

### 1. Get Daily Need Entry

Retrieve existing daily need entry for a gate entry.

```
GET /api/v1/daily-needs-gatein/gate-entries/{gate_entry_id}/daily-need/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `daily_needs_gatein.can_view_daily_need_entry`

**Response (200 OK):**
```json
{
    "id": 1,
    "item_category": {
        "id": 1,
        "category_name": "CANTEEN"
    },
    "supplier_name": "Fresh Veg Supplier",
    "material_name": "Vegetables",
    "quantity": "50.00",
    "unit": "KG",
    "receiving_department": 1,
    "bill_number": "BILL-4587",
    "delivery_challan_number": "DC-4587",
    "canteen_supervisor": "Ramesh",
    "vehicle_or_person_name": "Tempo DL01AB2233",
    "contact_number": "9876543210",
    "remarks": "Morning supply"
}
```

**Error Response (404):**
```json
{
    "detail": "Daily need entry does not exist"
}
```

---

### 2. Create Daily Need Entry

Create new daily need gate entry for a vehicle entry.

```
POST /api/v1/daily-needs-gatein/gate-entries/{gate_entry_id}/daily-need/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `daily_needs_gatein.can_create_daily_need_entry`

**Request Body:**
```json
{
    "item_category": 1,
    "supplier_name": "Fresh Veg Supplier",
    "material_name": "Vegetables",
    "quantity": 50.00,
    "unit": "KG",
    "receiving_department": 1,
    "bill_number": "BILL-4587",
    "delivery_challan_number": "DC-4587",
    "canteen_supervisor": "Ramesh",
    "vehicle_or_person_name": "Tempo DL01AB2233",
    "contact_number": "9876543210",
    "remarks": "Morning supply"
}
```

**Response (201 Created):**
```json
{
    "message": "Daily need gate entry created",
    "id": 1
}
```

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Invalid entry type. Expected DAILY_NEED.` |
| 400 | `Gate entry is locked` |
| 400 | `Daily need entry already exists` |
| 403 | `You do not have permission to perform this action.` |

---

### 3. Complete Daily Need Entry

Complete and lock a daily need gate entry.

```
POST /api/v1/daily-needs-gatein/gate-entries/{gate_entry_id}/complete/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `daily_needs_gatein.can_complete_daily_need_entry`

**Request Body:** None required

**Response (200 OK):**
```json
{
    "detail": "Daily need gate entry completed successfully"
}
```

**Validation Rules:**
- Entry type must be `DAILY_NEED`
- Security check must exist
- Daily need entry must exist
- No QC or weighment required

---

### 4. List Categories

List all categories for daily need / canteen items (for dropdown).

```
GET /api/v1/daily-needs-gatein/gate-entries/daily-need/categories/
```

**Permission Required:** `IsAuthenticated` + `daily_needs_gatein.can_view_category`

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "category_name": "CANTEEN"
    },
    {
        "id": 2,
        "category_name": "OFFICE_SUPPLIES"
    }
]
```

---

## Permission Summary

| Endpoint | Method | Permission Codename |
|----------|--------|---------------------|
| `/gate-entries/{id}/daily-need/` | GET | `can_view_daily_need_entry` |
| `/gate-entries/{id}/daily-need/` | POST | `can_create_daily_need_entry` |
| `/gate-entries/{id}/complete/` | POST | `can_complete_daily_need_entry` |
| `/gate-entries/daily-need/categories/` | GET | `can_view_category` |

## All Permissions

| Permission Codename | Description |
|---------------------|-------------|
| `daily_needs_gatein.can_create_daily_need_entry` | Can create daily need gate entry |
| `daily_needs_gatein.can_view_daily_need_entry` | Can view daily need gate entry |
| `daily_needs_gatein.can_edit_daily_need_entry` | Can edit daily need gate entry |
| `daily_needs_gatein.can_delete_daily_need_entry` | Can delete daily need gate entry |
| `daily_needs_gatein.can_complete_daily_need_entry` | Can complete daily need gate entry |
| `daily_needs_gatein.can_view_category` | Can view category |
| `daily_needs_gatein.can_manage_category` | Can manage category |

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
