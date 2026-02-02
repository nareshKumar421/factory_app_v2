# Construction Gate Pass Module

## Overview

The **Construction Gate Pass Module** (`construction_gatein`) handles gate entry management for Construction / Civil Work Materials. This module is linked to `VehicleEntry` with `entry_type="CONSTRUCTION"` and provides dedicated tracking for construction materials entering the factory premises.

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONSTRUCTION GATE PASS FLOW                               │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   STEP 1     │
    │ Create Gate  │──────► VehicleEntry created with entry_type="CONSTRUCTION"
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
    │ Construction │──────► POST /api/v1/construction-gatein/gate-entries/{id}/construction/
    │Entry Created │        - Contractor details
    └──────┬───────┘        - Material category & description
           │                - Quantity & unit
           │                - Project name (optional)
           ▼
    ┌──────────────┐
    │   STEP 4     │
    │   Update     │──────► PUT /api/v1/construction-gatein/gate-entries/{id}/construction/update/
    │   Entry      │        - Update any field
    └──────┬───────┘        - Set security_approval to APPROVED
           │                - Add site_engineer name
           ▼
    ┌──────────────┐
    │   STEP 5     │
    │  Complete    │──────► POST /api/v1/construction-gatein/gate-entries/{id}/complete/
    │  & Lock      │        Validates all business rules before locking
    └──────────────┘

```

---

## Business Rules (Completion Validation)

Before a construction gate entry can be completed and locked, the following conditions must be met:

| # | Rule | Description |
|---|------|-------------|
| 1 | Entry Type | Must be `CONSTRUCTION` |
| 2 | Not Locked | Gate entry must not already be locked |
| 3 | Security Check | Security check must exist and be submitted |
| 4 | Construction Entry | Construction entry must be created |
| 5 | Security Approval | Must be `APPROVED` (not `PENDING` or `REJECTED`) |
| 6 | Site Engineer | Site engineer name is required |
| 7 | Material Category | Material category must be selected |
| 8 | Contractor Name | Contractor name is required |

---

## Models

### ConstructionMaterialCategory (Lookup Table)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `category_name` | CharField(100) | Yes | Unique category name |
| `description` | TextField | No | Category description |
| `is_active` | BooleanField | Yes | Default: True |

**Initial Categories:**
- Cement
- Steel/Rebar
- Bricks/Blocks
- Sand
- Aggregate/Gravel
- Pipes/Fittings
- Electrical Materials
- Tiles/Flooring
- Paint/Finishing
- Wood/Timber
- Other

### ConstructionGateEntry (Main Model)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `vehicle_entry` | OneToOneField | Yes | FK to VehicleEntry (CASCADE) |
| `project_name` | CharField(200) | No | Project/Work Order Name |
| `work_order_number` | CharField(20) | Auto | Format: WO-YYYY-NNN |
| `contractor_name` | CharField(200) | Yes | Contractor company name |
| `contractor_contact` | CharField(15) | No | Phone with validation |
| `material_category` | ForeignKey | Yes | FK to lookup table |
| `material_description` | TextField | Yes | Min 5 characters |
| `quantity` | Decimal(10,2) | Yes | Min 0.01 |
| `unit` | CharField(10) | Yes | PCS/KG/LTR/BOX |
| `challan_number` | CharField(100) | No | Delivery challan |
| `invoice_number` | CharField(100) | No | Invoice reference |
| `site_engineer` | CharField(100) | Yes* | Required for completion |
| `security_approval` | CharField(10) | Yes | PENDING/APPROVED/REJECTED |
| `remarks` | TextField | No | Additional notes |
| `inward_time` | DateTimeField | Auto | auto_now_add |
| `created_by` | ForeignKey | Auto | FK to User |
| `created_at` | DateTimeField | Auto | auto_now_add |

---

## API Documentation

### Base URL
```
/api/v1/construction-gatein/
```

### Authentication
All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

### Headers Required
```
Authorization: Bearer <jwt_token>
Company-Code: <company_code>
Content-Type: application/json
```

---

### 1. Get/Create Construction Entry

#### GET - Retrieve Construction Entry
```
GET /api/v1/construction-gatein/gate-entries/{gate_entry_id}/construction/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "project_name": "Building A Extension",
    "work_order_number": "WO-2026-001",
    "contractor_name": "ABC Constructions Pvt Ltd",
    "contractor_contact": "+919876543210",
    "material_category": {
        "id": 1,
        "category_name": "Cement"
    },
    "material_description": "50kg Portland Cement Bags - Grade 53",
    "quantity": "100.00",
    "unit": "BOX",
    "challan_number": "CH-2026-001",
    "invoice_number": "INV-2026-001",
    "site_engineer": "Ramesh Kumar",
    "security_approval": "APPROVED",
    "remarks": "For foundation work",
    "inward_time": "2026-01-28T10:30:00Z"
}
```

**Error Response (404):**
```json
{
    "detail": "Construction entry does not exist"
}
```

---

#### POST - Create Construction Entry
```
POST /api/v1/construction-gatein/gate-entries/{gate_entry_id}/construction/
```

**Request Body:**
```json
{
    "contractor_name": "ABC Constructions Pvt Ltd",
    "contractor_contact": "+919876543210",
    "material_category": 1,
    "material_description": "50kg Portland Cement Bags - Grade 53",
    "quantity": 100,
    "unit": "BOX",
    "project_name": "Building A Extension",
    "challan_number": "CH-2026-001",
    "invoice_number": "INV-2026-001",
    "remarks": "For foundation work"
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
| 400 | `Quantity must be a positive number` |
| 400 | `Material description must be at least 5 characters` |

---

### 2. Update Construction Entry

```
PUT /api/v1/construction-gatein/gate-entries/{gate_entry_id}/construction/update/
```

**Request Body (Partial Update Supported):**
```json
{
    "site_engineer": "Ramesh Kumar",
    "security_approval": "APPROVED",
    "quantity": 150,
    "remarks": "Quantity increased as per revised order"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "project_name": "Building A Extension",
    "work_order_number": "WO-2026-001",
    "contractor_name": "ABC Constructions Pvt Ltd",
    "contractor_contact": "+919876543210",
    "material_category": {
        "id": 1,
        "category_name": "Cement"
    },
    "material_description": "50kg Portland Cement Bags - Grade 53",
    "quantity": "150.00",
    "unit": "BOX",
    "challan_number": "CH-2026-001",
    "invoice_number": "INV-2026-001",
    "site_engineer": "Ramesh Kumar",
    "security_approval": "APPROVED",
    "remarks": "Quantity increased as per revised order",
    "inward_time": "2026-01-28T10:30:00Z"
}
```

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Gate entry is locked` |
| 404 | `Construction entry does not exist` |

---

### 3. Complete & Lock Entry

```
POST /api/v1/construction-gatein/gate-entries/{gate_entry_id}/complete/
```

**Request Body:** None required

**Response (200 OK):**
```json
{
    "detail": "Construction gate entry completed successfully"
}
```

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Gate entry already completed` |
| 400 | `Invalid entry type for construction completion` |
| 400 | `Security check not completed` |
| 400 | `Security check not submitted` |
| 400 | `Construction entry not filled` |
| 400 | `Security approval is PENDING. Must be APPROVED to complete.` |
| 400 | `Site engineer name is required for completion` |
| 400 | `Material category must be selected` |
| 400 | `Contractor name is required` |

---

### 4. List Material Categories

```
GET /api/v1/construction-gatein/gate-entries/construction/categories/
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "category_name": "Cement",
        "description": "Portland cement, white cement, and other cement types",
        "is_active": true
    },
    {
        "id": 2,
        "category_name": "Steel/Rebar",
        "description": "Reinforcement bars, steel rods, and structural steel",
        "is_active": true
    }
    // ... more categories
]
```

---

### 5. Full Entry View (Read-Only)

```
GET /api/v1/gate-core/construction-gate-entry/{gate_entry_id}/
```

**Response (200 OK):**
```json
{
    "gate_entry": {
        "id": 1,
        "entry_no": "GE-2026-001",
        "status": "COMPLETED",
        "is_locked": true,
        "created_at": "2026-01-28T10:00:00Z",
        "entry_type": "CONSTRUCTION"
    },
    "vehicle": {
        "vehicle_number": "MP09AB1234",
        "vehicle_type": "TRUCK",
        "capacity_ton": 10.0
    },
    "driver": {
        "name": "Suresh Kumar",
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
    "construction_details": {
        "work_order_number": "WO-2026-001",
        "project_name": "Building A Extension",
        "material_category": "Cement",
        "contractor_name": "ABC Constructions Pvt Ltd",
        "contractor_contact": "+919876543210",
        "material_description": "50kg Portland Cement Bags - Grade 53",
        "quantity": 100.0,
        "unit": "BOX",
        "challan_number": "CH-2026-001",
        "invoice_number": "INV-2026-001",
        "site_engineer": "Ramesh Kumar",
        "security_approval": "APPROVED",
        "inward_time": "2026-01-28T10:30:00Z",
        "remarks": "For foundation work",
        "created_by": "operator@factory.com",
        "created_at": "2026-01-28T10:30:00Z"
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

## Security Approval Status

| Code | Display | Can Complete? |
|------|---------|---------------|
| `PENDING` | Pending | No |
| `APPROVED` | Approved | Yes |
| `REJECTED` | Rejected | No |

---

## Module Structure

```
construction_gatein/
├── __init__.py
├── apps.py
├── models.py                    # ConstructionMaterialCategory, ConstructionGateEntry
├── serializers.py               # Validation & serialization
├── views.py                     # 4 API endpoints
├── urls.py                      # URL routing
├── admin.py                     # Enhanced admin interface
├── README.md                    # This documentation
├── migrations/
│   ├── __init__.py
│   ├── 0001_initial.py          # Schema migration
│   └── 0002_seed_initial_categories.py  # Seed data
└── services/
    ├── __init__.py
    └── construction_completion.py  # Business logic
```

---

## Admin Interface

The module provides a comprehensive admin interface with:

- **ConstructionMaterialCategory Admin**
  - List view with entry count links
  - Search by name and description
  - Filter by active status

- **ConstructionGateEntry Admin**
  - Colored badges for unit and security approval status
  - Clickable links to related vehicle entry and category
  - Date hierarchy for quick navigation
  - Advanced search across multiple fields
  - Optimized queries with select_related

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `driver_management` | Parent VehicleEntry model |
| `security_checks` | Security inspection data |
| `gate_core` | Full entry view API |
| `accounts` | User authentication |
| `company` | Company context permission |
