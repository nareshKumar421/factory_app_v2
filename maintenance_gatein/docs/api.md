# Maintenance Gate-In API Documentation

## Base URL
```
/api/v1/maintenance-gatein/
```

## Headers Required
```
Authorization: Bearer <access_token>
Company-Code: <company_code>
```

---

## Endpoints

### 1. Get Maintenance Entry

Retrieve existing maintenance entry for a gate entry.

```
GET /api/v1/maintenance-gatein/gate-entries/{gate_entry_id}/maintenance/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `maintenance_gatein.view_maintenancegateentry`

**Response (200 OK):**
```json
{
    "id": 1,
    "maintenance_type": {
        "id": 1,
        "type_name": "Electrical"
    },
    "work_order_number": "MO-2026-001",
    "supplier_name": "ABC Electricals",
    "material_description": "Motor Spare Parts",
    "part_number": "MSP-001",
    "quantity": "5.00",
    "unit": "PCS",
    "invoice_number": "INV-001",
    "equipment_id": "EQ-101",
    "receiving_department": 1,
    "urgency_level": "HIGH",
    "remarks": ""
}
```

**Error Response (404):**
```json
{
    "detail": "Maintenance entry does not exist"
}
```

---

### 2. Create Maintenance Entry

Create new maintenance gate entry for a vehicle entry.

```
POST /api/v1/maintenance-gatein/gate-entries/{gate_entry_id}/maintenance/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `maintenance_gatein.add_maintenancegateentry`

**Request Body:**
```json
{
    "maintenance_type": 1,
    "supplier_name": "ABC Electricals",
    "material_description": "Motor Spare Parts",
    "part_number": "MSP-001",
    "quantity": 5.00,
    "unit": "PCS",
    "invoice_number": "INV-001",
    "equipment_id": "EQ-101",
    "receiving_department": 1,
    "urgency_level": "HIGH",
    "remarks": ""
}
```

**Response (201 Created):**
```json
{
    "message": "Maintenance gate entry created",
    "id": 1,
    "work_order_number": "MO-2026-001"
}
```

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Invalid entry type. Expected MAINTENANCE.` |
| 400 | `Gate entry is locked` |
| 400 | `Maintenance entry already exists` |
| 403 | `You do not have permission to perform this action.` |

---

### 3. Update Maintenance Entry

Update existing maintenance gate entry.

```
PUT /api/v1/maintenance-gatein/gate-entries/{gate_entry_id}/maintenance/update/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `maintenance_gatein.change_maintenancegateentry`

**Request Body:** (partial update supported)
```json
{
    "quantity": 10.00,
    "remarks": "Updated quantity"
}
```

**Response (200 OK):** Returns updated entry data.

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Gate entry is locked` |
| 403 | `You do not have permission to perform this action.` |
| 404 | `Maintenance entry does not exist` |

---

### 4. Complete Maintenance Entry

Complete and lock a maintenance gate entry.

```
POST /api/v1/maintenance-gatein/gate-entries/{gate_entry_id}/complete/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `maintenance_gatein.can_complete_maintenance_entry`

**Request Body:** None required

**Response (200 OK):**
```json
{
    "detail": "Maintenance gate entry completed successfully"
}
```

---

### 5. List Maintenance Types

List all active maintenance types (for dropdown).

```
GET /api/v1/maintenance-gatein/gate-entries/maintenance/types/
```

**Permission Required:** `IsAuthenticated` + `maintenance_gatein.view_maintenancetype`

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "type_name": "Electrical",
        "description": "Electrical maintenance and repair",
        "is_active": true
    },
    {
        "id": 2,
        "type_name": "Mechanical",
        "description": "Mechanical maintenance and repair",
        "is_active": true
    }
]
```

---

## Permission Summary

| Endpoint | Method | Permission Codename |
|----------|--------|---------------------|
| `/gate-entries/{id}/maintenance/` | GET | `view_maintenancegateentry` |
| `/gate-entries/{id}/maintenance/` | POST | `add_maintenancegateentry` |
| `/gate-entries/{id}/maintenance/update/` | PUT | `change_maintenancegateentry` |
| `/gate-entries/{id}/complete/` | POST | `can_complete_maintenance_entry` |
| `/gate-entries/maintenance/types/` | GET | `view_maintenancetype` |

## All Permissions

| Permission Codename | Description |
|---------------------|-------------|
| `maintenance_gatein.add_maintenancegateentry` | Can add maintenance gate entry |
| `maintenance_gatein.view_maintenancegateentry` | Can view maintenance gate entry |
| `maintenance_gatein.change_maintenancegateentry` | Can change maintenance gate entry |
| `maintenance_gatein.delete_maintenancegateentry` | Can delete maintenance gate entry |
| `maintenance_gatein.can_complete_maintenance_entry` | Can complete maintenance gate entry |
| `maintenance_gatein.view_maintenancetype` | Can view maintenance type |
| `maintenance_gatein.can_manage_maintenance_type` | Can manage maintenance type |

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
