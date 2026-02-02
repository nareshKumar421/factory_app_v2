# Security Checks Module

## Overview

The **Security Checks Module** handles vehicle and driver security inspections at the gate. It validates vehicle conditions, performs alcohol tests, and records seal information before allowing entry.

---

## Models

### SecurityCheck

| Field | Type | Description |
|-------|------|-------------|
| `vehicle_entry` | OneToOneField | Link to VehicleEntry (CASCADE) |
| `vehicle_condition_ok` | BooleanField | Vehicle condition status (default: True) |
| `tyre_condition_ok` | BooleanField | Tyre condition status (default: True) |
| `fire_extinguisher_available` | BooleanField | Fire extinguisher present (default: True) |
| `seal_no_before` | CharField(50) | Seal number before unloading |
| `seal_no_after` | CharField(50) | Seal number after unloading |
| `alcohol_test_done` | BooleanField | Alcohol test performed (default: False) |
| `alcohol_test_passed` | BooleanField | Alcohol test result (default: True) |
| `inspected_by_name` | CharField(100) | Inspector's name |
| `inspection_time` | DateTimeField | Auto-generated |
| `remarks` | TextField | Additional notes |
| `is_submitted` | BooleanField | Submission lock (default: False) |
| `created_at` | DateTimeField | Auto-generated |
| `created_by` | ForeignKey | User who created |

**Lock Behavior:** Once `is_submitted=True`, the security check cannot be modified.

---

## API Documentation

### Base URL
```
/api/v1/security-checks/
```

### Headers Required
```
Authorization: Bearer <access_token>
Company-Code: <company_code>
```

---

### 1. Create/Update Security Check

```
POST /api/v1/security-checks/gate-entries/{gate_entry_id}/security/
```

**Request Body:**
```json
{
    "vehicle_condition_ok": true,
    "tyre_condition_ok": true,
    "fire_extinguisher_available": true,
    "seal_no_before": "SEAL-001",
    "alcohol_test_done": true,
    "alcohol_test_passed": true,
    "inspected_by_name": "Security Guard 1",
    "remarks": "All checks passed"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "vehicle_condition_ok": true,
    "tyre_condition_ok": true,
    "fire_extinguisher_available": true,
    "seal_no_before": "SEAL-001",
    "seal_no_after": "",
    "alcohol_test_done": true,
    "alcohol_test_passed": true,
    "inspected_by_name": "Security Guard 1",
    "inspection_time": "2026-01-15T10:00:00Z",
    "remarks": "All checks passed",
    "is_submitted": false
}
```

**Note:** This endpoint creates a new security check if one doesn't exist, or updates the existing one. It also changes the gate entry status from `DRAFT` to `IN_PROGRESS`.

---

### 2. Get Security Check Details

```
GET /api/v1/security-checks/gate-entries/{gate_entry_id}/security/view/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "vehicle_condition_ok": true,
    "tyre_condition_ok": true,
    "fire_extinguisher_available": true,
    "seal_no_before": "SEAL-001",
    "seal_no_after": "",
    "alcohol_test_done": true,
    "alcohol_test_passed": true,
    "inspected_by_name": "Security Guard 1",
    "inspection_time": "2026-01-15T10:00:00Z",
    "remarks": "All checks passed",
    "is_submitted": false
}
```

**Error Response (404):**
```json
{
    "detail": "Security check not found"
}
```

---

### 3. Submit Security Check (Lock)

```
POST /api/v1/security-checks/security/{security_id}/submit/
```

**Request Body:** None required

**Response (200 OK):**
```json
{
    "message": "Security check submitted successfully"
}
```

**Error Response (400):**
```json
{
    "detail": "Security check already submitted"
}
```

**Note:** Once submitted, the security check cannot be modified.

---

## Security Check Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      SECURITY CHECK FLOW                                  │
└──────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │ Gate Entry   │
    │   Created    │ ──► Status: DRAFT
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Security   │
    │ Check Start  │ ──► POST /gate-entries/{id}/security/
    └──────┬───────┘     Status changes to: IN_PROGRESS
           │
           ▼
    ┌──────────────┐
    │  Inspection  │
    │   Updates    │ ──► Update vehicle condition, alcohol test, etc.
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │    Submit    │
    │    Check     │ ──► POST /security/{id}/submit/
    └──────┬───────┘     is_submitted = True (LOCKED)
           │
           ▼
    ┌──────────────┐
    │  Proceed to  │
    │  Next Step   │ ──► Weighment / PO Receipt / Module-specific entry
    └──────────────┘
```

---

## Inspection Checklist

| Check | Description |
|-------|-------------|
| Vehicle Condition | Overall vehicle condition inspection |
| Tyre Condition | All tyres properly inflated and undamaged |
| Fire Extinguisher | Fire extinguisher available and valid |
| Seal Before | Container/truck seal number before unloading |
| Seal After | New seal number after loading (if applicable) |
| Alcohol Test | Driver alcohol breath test |

---

## Module Structure

```
security_checks/
├── __init__.py
├── apps.py
├── models/
│   ├── __init__.py
│   └── security_check.py   # SecurityCheck model
├── serializers.py          # SecurityCheckSerializer
├── views.py                # API views
├── urls.py                 # URL routing
├── admin.py                # Admin configuration
└── migrations/
```
