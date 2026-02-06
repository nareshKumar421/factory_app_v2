# Gate Core API Documentation

## Base URL
```
/api/v1/gate-core/
```

## Headers Required
```
Authorization: Bearer <access_token>
Company-Code: <company_code>
```

---

## Endpoints

All endpoints are **read-only** full detail views combining data from multiple modules (gate entry, vehicle, driver, security, weighment, QC, etc.)

### 1. Raw Material Gate Entry Full View

Get complete raw material gate entry data including QC status summary.

```
GET /api/v1/gate-core/raw-material-gate-entry/{gate_entry_id}/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `gate_core.can_view_raw_material_full_entry`

**Response (200 OK):**
```json
{
    "gate_entry": {
        "id": 1,
        "entry_no": "GE-2026-001",
        "entry_type": "RAW_MATERIAL",
        "status": "QC_PENDING",
        "is_locked": false,
        "created_at": "2026-01-01T10:00:00Z"
    },
    "vehicle": {
        "id": 1,
        "vehicle_number": "DL01AB1234",
        "vehicle_type": "TRUCK",
        "capacity_ton": 10.0
    },
    "driver": {
        "id": 1,
        "name": "John Doe",
        "mobile_no": "9876543210",
        "license_no": "DL123456"
    },
    "security_check": { "..." : "..." },
    "weighment": { "..." : "..." },
    "qc_summary": {
        "total_items": 2,
        "accepted": 1,
        "rejected": 0,
        "pending": 1,
        "can_complete": false
    },
    "po_receipts": [ "..." ]
}
```

---

### 2. Daily Need Gate Entry Full View

Get complete daily need / canteen gate entry data.

```
GET /api/v1/gate-core/daily-need-gate-entry/{gate_entry_id}/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `gate_core.can_view_daily_need_full_entry`

**Response (200 OK):**
```json
{
    "gate_entry": {
        "id": 2,
        "entry_no": "GE-2026-002",
        "status": "COMPLETED",
        "is_locked": true,
        "entry_type": "DAILY_NEED"
    },
    "vehicle": { "..." : "..." },
    "driver": { "..." : "..." },
    "security_check": { "..." : "..." },
    "daily_need_details": {
        "category": "CANTEEN",
        "supplier_name": "Fresh Veg Supplier",
        "material_name": "Vegetables",
        "quantity": 50.0,
        "unit": "KG",
        "receiving_department": "Canteen"
    }
}
```

---

### 3. Maintenance Gate Entry Full View

Get complete maintenance & repair material gate entry data.

```
GET /api/v1/gate-core/maintenance-gate-entry/{gate_entry_id}/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `gate_core.can_view_maintenance_full_entry`

**Response (200 OK):**
```json
{
    "gate_entry": {
        "id": 3,
        "entry_no": "GE-2026-003",
        "status": "IN_PROGRESS",
        "is_locked": false,
        "entry_type": "MAINTENANCE"
    },
    "vehicle": { "..." : "..." },
    "driver": { "..." : "..." },
    "security_check": { "..." : "..." },
    "maintenance_details": {
        "work_order_number": "MO-2026-001",
        "maintenance_type": "Electrical",
        "supplier_name": "ABC Electricals",
        "material_description": "Motor Spare Parts",
        "quantity": 5.0,
        "unit": "PCS"
    }
}
```

---

### 4. Construction Gate Entry Full View

Get complete construction / civil work material gate entry data.

```
GET /api/v1/gate-core/construction-gate-entry/{gate_entry_id}/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `gate_core.can_view_construction_full_entry`

**Response (200 OK):**
```json
{
    "gate_entry": {
        "id": 4,
        "entry_no": "GE-2026-004",
        "status": "IN_PROGRESS",
        "is_locked": false,
        "entry_type": "CONSTRUCTION"
    },
    "vehicle": { "..." : "..." },
    "driver": { "..." : "..." },
    "security_check": { "..." : "..." },
    "construction_details": {
        "work_order_number": "WO-2026-001",
        "project_name": "Factory Expansion",
        "material_category": "Cement",
        "contractor_name": "ABC Construction",
        "material_description": "OPC 53 Grade Cement",
        "quantity": 500.0,
        "unit": "KG"
    }
}
```

---

## Permission Summary

| Endpoint | Method | Permission Codename |
|----------|--------|---------------------|
| `/raw-material-gate-entry/{id}/` | GET | `can_view_raw_material_full_entry` |
| `/daily-need-gate-entry/{id}/` | GET | `can_view_daily_need_full_entry` |
| `/maintenance-gate-entry/{id}/` | GET | `can_view_maintenance_full_entry` |
| `/construction-gate-entry/{id}/` | GET | `can_view_construction_full_entry` |

## All Permissions

| Permission Codename | Description |
|---------------------|-------------|
| `gate_core.can_view_gate_entry` | Can view gate entry |
| `gate_core.can_view_raw_material_full_entry` | Can view full raw material gate entry |
| `gate_core.can_view_daily_need_full_entry` | Can view full daily need gate entry |
| `gate_core.can_view_maintenance_full_entry` | Can view full maintenance gate entry |
| `gate_core.can_view_construction_full_entry` | Can view full construction gate entry |

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
    "detail": "Gate entry not found"
}
```
