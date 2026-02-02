# Quality Control Module

## Overview

The **Quality Control Module** handles quality inspection for raw material PO items. It tracks sample collection, batch information, and QC pass/fail status for each received item.

---

## Models

### QCInspection

| Field | Type | Description |
|-------|------|-------------|
| `po_item_receipt` | OneToOneField | Link to POItemReceipt (CASCADE) |
| `qc_status` | CharField(20) | QC result status |
| `sample_collected` | BooleanField | Sample collection flag (default: False) |
| `batch_no` | CharField(50) | Batch/lot number |
| `expiry_date` | DateField | Product expiry date |
| `inspected_by` | ForeignKey | QC inspector (User) |
| `inspection_time` | DateTimeField | Auto-generated |
| `remarks` | TextField | QC notes/observations |
| `is_locked` | BooleanField | Lock status (default: False) |
| `created_at` | DateTimeField | Auto-generated |
| `created_by` | ForeignKey | User who created |

**QC Status Choices:**

| Code | Display | Locks Record |
|------|---------|--------------|
| `PENDING` | Pending | No |
| `PASSED` | Passed | Yes |
| `FAILED` | Failed | Yes |

**Lock Behavior:** Once status is `PASSED` or `FAILED`, the record is locked and cannot be modified.

---

## API Documentation

### Base URL
```
/api/v1/quality-control/
```

### Headers Required
```
Authorization: Bearer <access_token>
```

---

### 1. Create/Update QC Inspection

```
POST /api/v1/quality-control/po-items/{po_item_id}/qc/
```

**Request Body:**
```json
{
    "qc_status": "PENDING",
    "sample_collected": true,
    "batch_no": "BATCH-2026-001",
    "expiry_date": "2027-01-15",
    "remarks": "Sample sent to lab for testing"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "qc_status": "PENDING",
    "sample_collected": true,
    "batch_no": "BATCH-2026-001",
    "expiry_date": "2027-01-15",
    "inspected_by": 1,
    "inspection_time": "2026-01-15T10:00:00Z",
    "remarks": "Sample sent to lab for testing",
    "is_locked": false
}
```

**Request Body (Final QC Decision):**
```json
{
    "qc_status": "PASSED",
    "remarks": "All quality parameters within acceptable limits"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "qc_status": "PASSED",
    "sample_collected": true,
    "batch_no": "BATCH-2026-001",
    "expiry_date": "2027-01-15",
    "inspected_by": 1,
    "inspection_time": "2026-01-15T10:00:00Z",
    "remarks": "All quality parameters within acceptable limits",
    "is_locked": true
}
```

**Note:**
- This endpoint creates a new QC inspection if one doesn't exist, or updates the existing one
- Setting status to `PASSED` or `FAILED` automatically locks the record
- When all QC inspections for a gate entry are completed, the entry status changes to `QC_COMPLETED`

---

### 2. Get QC Inspection Details

```
GET /api/v1/quality-control/po-items/{po_item_id}/qc/view/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "qc_status": "PASSED",
    "sample_collected": true,
    "batch_no": "BATCH-2026-001",
    "expiry_date": "2027-01-15",
    "inspected_by": 1,
    "inspection_time": "2026-01-15T10:00:00Z",
    "remarks": "All quality parameters within acceptable limits",
    "is_locked": true
}
```

**Error Response (404):**
```json
{
    "detail": "QC not found"
}
```

---

## QC Inspection Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                       QC INSPECTION FLOW                                  │
└──────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │  PO Items    │
    │  Received    │ ──► Gate entry status: QC_PENDING
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Sample     │
    │ Collection   │ ──► sample_collected = true
    └──────┬───────┘     Record batch_no, expiry_date
           │
           ▼
    ┌──────────────┐
    │  Lab Testing │
    │   (Manual)   │ ──► Physical/chemical analysis
    └──────┬───────┘
           │
           ├─────────────────────────────────────┐
           │                                     │
           ▼                                     ▼
    ┌──────────────┐                    ┌──────────────┐
    │    PASSED    │                    │    FAILED    │
    │  is_locked   │                    │  is_locked   │
    └──────┬───────┘                    └──────┬───────┘
           │                                     │
           └─────────────────┬───────────────────┘
                             │
                             ▼
                    ┌──────────────┐
                    │ All Items    │
                    │  Inspected?  │ ──► Yes: Status changes to QC_COMPLETED
                    └──────────────┘
```

---

## Auto-Status Update

When all PO items for a gate entry have QC status of `PASSED` or `FAILED`:
- Gate entry status automatically changes from `QC_PENDING` to `QC_COMPLETED`
- This is handled by the `check_and_mark_qc_completed` service

---

## Module Structure

```
quality_control/
├── __init__.py
├── apps.py
├── models/
│   ├── __init__.py
│   └── qc_inspection.py    # QCInspection model
├── enums.py                # QCStatus choices
├── serializers.py          # QCInspectionSerializer
├── views.py                # API views
├── urls.py                 # URL routing
├── services/
│   ├── __init__.py
│   └── qc_completion.py    # Auto-status update service
├── admin.py                # Admin configuration
└── migrations/
```

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `raw_material_gatein` | Parent POItemReceipt |
| `driver_management` | VehicleEntry status updates |
