# Gate Core Module

## Overview

The **Gate Core Module** provides base models, enums, and full-view APIs for the gate management system. It contains abstract base classes used by all other gate-related modules.

---

## Base Models

### BaseModel (Abstract)

| Field | Type | Description |
|-------|------|-------------|
| `created_at` | DateTimeField | Auto-generated on creation |
| `updated_at` | DateTimeField | Auto-updated on save |
| `created_by` | ForeignKey | User who created |
| `updated_by` | ForeignKey | User who last updated |
| `is_active` | BooleanField | Active status (default: True) |

### GateEntryBase (Abstract)

Extends `BaseModel` with:

| Field | Type | Description |
|-------|------|-------------|
| `entry_no` | CharField(30) | Unique entry number |
| `status` | CharField(20) | Entry status |
| `is_locked` | BooleanField | Lock status (default: False) |

**Lock Protection:** Once `is_locked=True`, the entry cannot be modified.

---

## Enums

### GateEntryStatus

| Code | Display |
|------|---------|
| `DRAFT` | Draft |
| `SECURITY_CHECK_DONE` | Security Check Done |
| `ARRIVAL_SLIP_SUBMITTED` | Arrival Slip Submitted |
| `ARRIVAL_SLIP_REJECTED` | Arrival Slip Rejected |
| `IN_PROGRESS` | In Progress |
| `QC_PENDING` | QC Pending |
| `QC_IN_REVIEW` | QC In Review |
| `QC_AWAITING_QAM` | Awaiting QAM Approval |
| `QC_COMPLETED` | QC Completed |
| `COMPLETED` | Completed |
| `CANCELLED` | Cancelled |

---

## API Documentation

### Base URL
```
/api/v1/gate-core/
```

### Headers Required
```
Authorization: Bearer <access_token>
Company-Code: <company_code>
```

---

### 1. Raw Material Gate Entry Full View

```
GET /api/v1/gate-core/raw-material-gate-entry/{gate_entry_id}/
```

**Response (200 OK):**
```json
{
    "gate_entry": {
        "id": 1,
        "entry_no": "GE-2026-001",
        "status": "COMPLETED",
        "is_locked": true,
        "created_at": "2026-01-15T10:00:00Z"
    },
    "vehicle": {
        "vehicle_number": "MP09AB1234",
        "vehicle_type": "TRUCK",
        "capacity_ton": 10.0
    },
    "driver": {
        "name": "Ramesh Kumar",
        "mobile_no": "9876543210",
        "license_no": "MP0920210012345"
    },
    "security_check": {
        "vehicle_condition_ok": true,
        "tyre_condition_ok": true,
        "fire_extinguisher_available": true,
        "alcohol_test_done": true,
        "alcohol_test_passed": true,
        "is_submitted": true,
        "remarks": null,
        "inspected_by": "Security Guard 1"
    },
    "weighment": {
        "gross_weight": 15000.000,
        "tare_weight": 5000.000,
        "net_weight": 10000.000,
        "weighbridge_slip_no": "WB-2026-001"
    },
    "po_receipts": [
        {
            "po_number": "PO-2026-001",
            "supplier_code": "SUP001",
            "supplier_name": "ABC Suppliers",
            "created_by": "operator@factory.com",
            "items": [
                {
                    "item_code": "ITEM001",
                    "item_name": "Raw Material A",
                    "ordered_qty": 1000.0,
                    "received_qty": 950.0,
                    "short_qty": 50.0,
                    "uom": "KG",
                    "arrival_slip": {
                        "id": 1,
                        "status": "SUBMITTED",
                        "is_submitted": true
                    },
                    "inspection": {
                        "id": 1,
                        "report_no": "RMI-2026-001",
                        "workflow_status": "COMPLETED",
                        "final_status": "ACCEPTED",
                        "remarks": "Quality approved"
                    }
                }
            ]
        }
    ]
}
```

---

### 2. Daily Need Gate Entry Full View

```
GET /api/v1/gate-core/daily-need-gate-entry/{gate_entry_id}/
```

**Response (200 OK):**
```json
{
    "gate_entry": {
        "id": 2,
        "entry_no": "GE-2026-002",
        "status": "COMPLETED",
        "is_locked": true,
        "created_at": "2026-01-15T11:00:00Z",
        "entry_type": "DAILY_NEED"
    },
    "vehicle": {
        "vehicle_number": "MP09CD5678",
        "vehicle_type": "TEMPO",
        "capacity_ton": 2.0
    },
    "driver": {
        "name": "Suresh Singh",
        "mobile_no": "9876543211",
        "license_no": "MP0920210012346"
    },
    "security_check": {
        "vehicle_condition_ok": true,
        "tyre_condition_ok": true,
        "alcohol_test_passed": true,
        "is_submitted": true,
        "remarks": null,
        "inspected_by": "Security Guard 2"
    },
    "daily_need_details": {
        "category": "Vegetables",
        "supplier_name": "Fresh Farms",
        "material_name": "Mixed Vegetables",
        "quantity": 50.0,
        "unit": "KG",
        "receiving_department": "Canteen",
        "bill_number": "BILL-001",
        "delivery_challan_number": "DC-001",
        "canteen_supervisor": "Mohan Kumar",
        "vehicle_or_person_name": "Delivery Van",
        "contact_number": "9876543212",
        "remarks": null,
        "created_by": "operator@factory.com",
        "created_at": "2026-01-15T11:00:00Z"
    }
}
```

---

### 3. Maintenance Gate Entry Full View

```
GET /api/v1/gate-core/maintenance-gate-entry/{gate_entry_id}/
```

**Response (200 OK):**
```json
{
    "gate_entry": {
        "id": 3,
        "entry_no": "GE-2026-003",
        "status": "COMPLETED",
        "is_locked": true,
        "created_at": "2026-01-15T12:00:00Z",
        "entry_type": "MAINTENANCE"
    },
    "vehicle": {
        "vehicle_number": "MP09EF9012",
        "vehicle_type": "TRUCK",
        "capacity_ton": 5.0
    },
    "driver": {
        "name": "Mahesh Yadav",
        "mobile_no": "9876543213",
        "license_no": "MP0920210012347"
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
        "inward_time": "2026-01-15T12:00:00Z",
        "remarks": "For pump replacement",
        "created_by": "operator@factory.com",
        "created_at": "2026-01-15T12:00:00Z"
    }
}
```

---

### 4. Construction Gate Entry Full View

```
GET /api/v1/gate-core/construction-gate-entry/{gate_entry_id}/
```

**Response (200 OK):**
```json
{
    "gate_entry": {
        "id": 4,
        "entry_no": "GE-2026-004",
        "status": "COMPLETED",
        "is_locked": true,
        "created_at": "2026-01-15T13:00:00Z",
        "entry_type": "CONSTRUCTION"
    },
    "vehicle": {
        "vehicle_number": "MP09GH3456",
        "vehicle_type": "TRUCK",
        "capacity_ton": 10.0
    },
    "driver": {
        "name": "Raju Sharma",
        "mobile_no": "9876543214",
        "license_no": "MP0920210012348"
    },
    "security_check": {
        "vehicle_condition_ok": true,
        "tyre_condition_ok": true,
        "alcohol_test_passed": true,
        "is_submitted": true,
        "remarks": null,
        "inspected_by": "Security Guard 2"
    },
    "construction_details": {
        "work_order_number": "WO-2026-002",
        "project_name": "Building A Extension",
        "material_category": "Cement",
        "contractor_name": "ABC Constructions Pvt Ltd",
        "contractor_contact": "+919876543210",
        "material_description": "50kg Portland Cement Bags",
        "quantity": 100.0,
        "unit": "BOX",
        "challan_number": "CH-2026-001",
        "invoice_number": "INV-2026-002",
        "site_engineer": "Ramesh Kumar",
        "security_approval": "APPROVED",
        "inward_time": "2026-01-15T13:00:00Z",
        "remarks": "For foundation work",
        "created_by": "operator@factory.com",
        "created_at": "2026-01-15T13:00:00Z"
    }
}
```

---

## Gate Completion Rules

A gate entry can be marked as **COMPLETED** when:

1. **Security check** is submitted
2. **Weighment** is completed
3. At least one **PO item** exists
4. All PO items have completed **QC inspection** (either ACCEPTED or REJECTED)

### QC Completion Flow

```
POItemReceipt
      | (OneToOne)
MaterialArrivalSlip (Security fills)
      | (OneToOne)
RawMaterialInspection (QA fills)
      |
Final Status: ACCEPTED or REJECTED → Gate can complete
```

---

## Module Structure

```
gate_core/
├── __init__.py
├── apps.py
├── models/
│   ├── __init__.py
│   ├── base.py             # BaseModel (abstract)
│   └── gate_entry.py       # GateEntryBase (abstract)
├── enums.py                # GateEntryStatus
├── services/
│   ├── __init__.py
│   ├── status_guard.py     # Status transition validation
│   └── lock_manager.py     # Lock management
├── views.py                # Full view APIs
├── urls.py                 # URL routing
├── admin.py                # Admin configuration
└── migrations/
```

---

## Related Modules

All gate entry modules inherit from `GateEntryBase`:
- `driver_management.VehicleEntry`

All models use `BaseModel` for audit fields:
- `security_checks.SecurityCheck`
- `raw_material_gatein.POReceipt`, `POItemReceipt`
- `weighment.Weighment`
- `quality_control.MaterialArrivalSlip`
- `quality_control.RawMaterialInspection`
- `quality_control.InspectionParameterResult`
- `daily_needs_gatein.DailyNeedGateEntry`
- `maintenance_gatein.MaintenanceGateEntry`
- `construction_gatein.ConstructionGateEntry`
