# Maintenance Gate-In Module

## Overview

The **Maintenance Gate-In Module** handles gate entry management for Maintenance & Repair Materials. This module is linked to `VehicleEntry` with `entry_type="MAINTENANCE"` and provides dedicated tracking for spare parts, repair materials, and maintenance supplies entering the factory.

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MAINTENANCE GATE PASS FLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   STEP 1     │
    │ Create Gate  │──────► VehicleEntry created with entry_type="MAINTENANCE"
    │    Entry     │        (via driver_management module)
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   STEP 2     │
    │  Security    │──────► Security guard performs vehicle inspection
    │    Check     │        (via security_checks module)
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   STEP 3     │
    │ Maintenance  │──────► POST /api/v1/maintenance-gatein/gate-entries/{id}/maintenance/
    │Entry Created │        - Supplier details
    └──────┬───────┘        - Maintenance type
           │                - Material description
           ▼
    ┌──────────────┐
    │   STEP 4     │
    │   Update     │──────► PUT /api/v1/maintenance-gatein/gate-entries/{id}/maintenance/update/
    │   Entry      │        - Update any field
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   STEP 5     │
    │  Complete    │──────► POST /api/v1/maintenance-gatein/gate-entries/{id}/complete/
    │  & Lock      │        Validates all business rules before locking
    └──────────────┘

```

---

## Business Rules (Completion Validation)

Before a maintenance gate entry can be completed and locked:

| # | Rule | Description |
|---|------|-------------|
| 1 | Entry Type | Must be `MAINTENANCE` |
| 2 | Not Locked | Gate entry must not already be locked |
| 3 | Security Check | Security check must exist and be submitted |
| 4 | Maintenance Entry | Maintenance entry must be created |

---

## Models

### MaintenanceType (Lookup Table)

| Field | Type | Description |
|-------|------|-------------|
| `type_name` | CharField(100) | Unique type name |
| `description` | TextField | Type description |
| `is_active` | BooleanField | Active status (default: True) |

**Common Types:**
- Electrical
- Mechanical
- Plumbing
- HVAC
- Civil
- Equipment Repair

### MaintenanceGateEntry (Main Model)

| Field | Type | Description |
|-------|------|-------------|
| `vehicle_entry` | OneToOneField | FK to VehicleEntry (CASCADE) |
| `maintenance_type` | ForeignKey | FK to MaintenanceType |
| `work_order_number` | CharField(20) | Auto-generated (WO-YYYY-NNN) |
| `supplier_name` | CharField(200) | Supplier/Vendor name |
| `material_description` | TextField | Material details (min 5 chars) |
| `part_number` | CharField(100) | Part/SKU number |
| `quantity` | DecimalField | Quantity (min 0.01) |
| `unit` | CharField(10) | PCS/KG/LTR/BOX |
| `invoice_number` | CharField(100) | Invoice reference |
| `equipment_id` | CharField(100) | Target equipment ID |
| `receiving_department` | ForeignKey | FK to Department |
| `urgency_level` | CharField(10) | NORMAL/HIGH/CRITICAL |
| `inward_time` | DateTimeField | Auto-generated |
| `remarks` | TextField | Additional notes |
| `created_by` | ForeignKey | FK to User |
| `created_at` | DateTimeField | Auto-generated |

---

## API Documentation

### Base URL
```
/api/v1/maintenance-gatein/
```

### Headers Required
```
Authorization: Bearer <access_token>
Company-Code: <company_code>
```

---

### 1. Get/Create Maintenance Entry

#### GET - Retrieve Maintenance Entry
```
GET /api/v1/maintenance-gatein/gate-entries/{gate_entry_id}/maintenance/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "maintenance_type": {
        "id": 1,
        "type_name": "Electrical"
    },
    "work_order_number": "WO-2026-001",
    "supplier_name": "Electrical Supplies Ltd",
    "material_description": "Industrial Motors - 5HP",
    "part_number": "MOTOR-5HP-001",
    "quantity": "2.00",
    "unit": "PCS",
    "invoice_number": "INV-2026-001",
    "equipment_id": "PUMP-001",
    "receiving_department": {
        "id": 1,
        "name": "Maintenance"
    },
    "urgency_level": "HIGH",
    "inward_time": "2026-01-15T10:00:00Z",
    "remarks": "For pump replacement"
}
```

**Error Response (404):**
```json
{
    "detail": "Maintenance entry does not exist"
}
```

---

#### POST - Create Maintenance Entry
```
POST /api/v1/maintenance-gatein/gate-entries/{gate_entry_id}/maintenance/
```

**Request Body:**
```json
{
    "maintenance_type": 1,
    "supplier_name": "Electrical Supplies Ltd",
    "material_description": "Industrial Motors - 5HP",
    "part_number": "MOTOR-5HP-001",
    "quantity": 2,
    "unit": "PCS",
    "invoice_number": "INV-2026-001",
    "equipment_id": "PUMP-001",
    "receiving_department": 1,
    "urgency_level": "HIGH",
    "remarks": "For pump replacement"
}
```

**Response (201 Created):**
```json
{
    "message": "Maintenance gate entry created",
    "id": 1,
    "work_order_number": "WO-2026-001"
}
```

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Invalid entry type. Expected MAINTENANCE.` |
| 400 | `Gate entry is locked` |
| 400 | `Maintenance entry already exists` |
| 400 | `Quantity must be a positive number` |
| 400 | `Material description must be at least 5 characters` |

---

### 2. Update Maintenance Entry

```
PUT /api/v1/maintenance-gatein/gate-entries/{gate_entry_id}/maintenance/update/
```

**Request Body (Partial Update):**
```json
{
    "urgency_level": "CRITICAL",
    "quantity": 3,
    "remarks": "Urgency increased - production impact"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "maintenance_type": {
        "id": 1,
        "type_name": "Electrical"
    },
    "work_order_number": "WO-2026-001",
    "supplier_name": "Electrical Supplies Ltd",
    "material_description": "Industrial Motors - 5HP",
    "part_number": "MOTOR-5HP-001",
    "quantity": "3.00",
    "unit": "PCS",
    "invoice_number": "INV-2026-001",
    "equipment_id": "PUMP-001",
    "receiving_department": {
        "id": 1,
        "name": "Maintenance"
    },
    "urgency_level": "CRITICAL",
    "inward_time": "2026-01-15T10:00:00Z",
    "remarks": "Urgency increased - production impact"
}
```

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Gate entry is locked` |
| 404 | `Maintenance entry does not exist` |

---

### 3. Complete & Lock Entry

```
POST /api/v1/maintenance-gatein/gate-entries/{gate_entry_id}/complete/
```

**Request Body:** None required

**Response (200 OK):**
```json
{
    "detail": "Maintenance gate entry completed successfully"
}
```

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Gate entry already completed` |
| 400 | `Invalid entry type for maintenance completion` |
| 400 | `Security check not completed` |
| 400 | `Security check not submitted` |
| 400 | `Maintenance entry not filled` |

---

### 4. List Maintenance Types

```
GET /api/v1/maintenance-gatein/gate-entries/maintenance/types/
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "type_name": "Electrical",
        "description": "Electrical components and repairs",
        "is_active": true
    },
    {
        "id": 2,
        "type_name": "Mechanical",
        "description": "Mechanical parts and repairs",
        "is_active": true
    }
]
```

---

### 5. Full Entry View (Read-Only)

```
GET /api/v1/gate-core/maintenance-gate-entry/{gate_entry_id}/
```

**Response (200 OK):**
```json
{
    "gate_entry": {
        "id": 1,
        "entry_no": "GE-2026-001",
        "status": "COMPLETED",
        "is_locked": true,
        "created_at": "2026-01-15T10:00:00Z",
        "entry_type": "MAINTENANCE"
    },
    "vehicle": {
        "vehicle_number": "MP09AB1234",
        "vehicle_type": "TRUCK",
        "capacity_ton": 5.0
    },
    "driver": {
        "name": "Ramesh Kumar",
        "mobile_no": "9876543210",
        "license_no": "MP0920210012345"
    },
    "security_check": {
        "vehicle_condition_ok": true,
        "tyre_condition_ok": true,
        "alcohol_test_passed": true,
        "is_submitted": true,
        "remarks": null,
        "inspected_by": "Security Guard 1"
    },
    "maintenance_details": {
        "work_order_number": "WO-2026-001",
        "maintenance_type": "Electrical",
        "supplier_name": "Electrical Supplies Ltd",
        "material_description": "Industrial Motors - 5HP",
        "part_number": "MOTOR-5HP-001",
        "quantity": 2.0,
        "unit": "PCS",
        "invoice_number": "INV-2026-001",
        "equipment_id": "PUMP-001",
        "receiving_department": "Maintenance",
        "urgency_level": "HIGH",
        "inward_time": "2026-01-15T10:00:00Z",
        "remarks": "For pump replacement",
        "created_by": "operator@factory.com",
        "created_at": "2026-01-15T10:00:00Z"
    }
}
```

---

## Unit Choices

| Code | Display |
|------|---------|
| `PCS` | Pieces |
| `KG` | Kilogram |
| `LTR` | Litre |
| `BOX` | Box |

---

## Urgency Levels

| Code | Display | Color |
|------|---------|-------|
| `NORMAL` | Normal | Green |
| `HIGH` | High | Orange |
| `CRITICAL` | Critical | Red |

---

## Module Structure

```
maintenance_gatein/
├── __init__.py
├── apps.py
├── models.py                    # MaintenanceType, MaintenanceGateEntry
├── serializers.py               # Validation & serialization
├── views.py                     # 4 API endpoints
├── urls.py                      # URL routing
├── admin.py                     # Enhanced admin interface
├── README.md                    # This documentation
├── migrations/
└── services/
    ├── __init__.py
    └── maintenance_completion.py  # Business logic
```

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `driver_management` | Parent VehicleEntry model |
| `security_checks` | Security inspection data |
| `gate_core` | Full entry view API |
| `accounts` | User authentication, Department |
| `company` | Company context permission |
