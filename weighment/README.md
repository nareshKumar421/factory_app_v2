# Weighment Module

## Overview

The **Weighment Module** handles vehicle weight measurement using weighbridge. It records gross weight (loaded vehicle), tare weight (empty vehicle), and automatically calculates net weight.

---

## Models

### Weighment

| Field | Type | Description |
|-------|------|-------------|
| `vehicle_entry` | OneToOneField | Link to VehicleEntry (CASCADE) |
| `gross_weight` | DecimalField | Weight of loaded vehicle (kg) |
| `tare_weight` | DecimalField | Weight of empty vehicle (kg) |
| `net_weight` | DecimalField | Auto-calculated (gross - tare) |
| `weighbridge_slip_no` | CharField(50) | Weighbridge slip reference |
| `first_weighment_time` | DateTimeField | Gross weight timestamp |
| `second_weighment_time` | DateTimeField | Tare weight timestamp |
| `remarks` | TextField | Additional notes |
| `created_at` | DateTimeField | Auto-generated |
| `created_by` | ForeignKey | User who created |

**Auto-calculation:** `net_weight = gross_weight - tare_weight`

---

## API Documentation

### Base URL
```
/api/v1/weighment/
```

### Headers Required
```
Authorization: Bearer <access_token>
Company-Code: <company_code>
```

---

### 1. Create/Update Weighment

```
POST /api/v1/weighment/gate-entries/{gate_entry_id}/weighment/
```

**Request Body (First Weighment - Gross):**
```json
{
    "gross_weight": 15000.000,
    "weighbridge_slip_no": "WB-2026-001",
    "first_weighment_time": "2026-01-15T10:00:00Z",
    "remarks": "First weighment completed"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "gross_weight": "15000.000",
    "tare_weight": null,
    "net_weight": "0.000"
}
```

**Request Body (Second Weighment - Tare):**
```json
{
    "tare_weight": 5000.000,
    "second_weighment_time": "2026-01-15T14:00:00Z"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "gross_weight": "15000.000",
    "tare_weight": "5000.000",
    "net_weight": "10000.000"
}
```

**Note:** This endpoint creates a new weighment if one doesn't exist, or updates the existing one. Partial updates are supported.

---

### 2. Get Weighment Details

```
GET /api/v1/weighment/gate-entries/{gate_entry_id}/weighment/view/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "gross_weight": "15000.000",
    "tare_weight": "5000.000",
    "net_weight": "10000.000",
    "weighbridge_slip_no": "WB-2026-001",
    "first_weighment_time": "2026-01-15T10:00:00Z",
    "second_weighment_time": "2026-01-15T14:00:00Z",
    "remarks": "First weighment completed"
}
```

**Error Response (404):**
```json
{
    "detail": "Weighment not found"
}
```

---

## Weighment Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         WEIGHMENT FLOW                                    │
└──────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   Vehicle    │
    │   Arrives    │ ──► Loaded with materials
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │    First     │
    │  Weighment   │ ──► Record gross_weight
    └──────┬───────┘     net_weight = 0 (temporary)
           │
           ▼
    ┌──────────────┐
    │  Unloading   │
    │  Materials   │ ──► Material received at warehouse
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Second     │
    │  Weighment   │ ──► Record tare_weight
    └──────┬───────┘     net_weight = gross - tare
           │
           ▼
    ┌──────────────┐
    │   Vehicle    │
    │    Exits     │ ──► Net weight verified
    └──────────────┘
```

---

## Weight Calculation Rules

| Scenario | Net Weight |
|----------|------------|
| Only gross_weight recorded | 0 (temporary) |
| Both gross & tare recorded | gross_weight - tare_weight |
| Neither recorded | 0 |

---

## Use Cases by Entry Type

| Entry Type | Weighment Required |
|------------|-------------------|
| RAW_MATERIAL | Yes (mandatory for completion) |
| DAILY_NEED | No |
| MAINTENANCE | No |
| CONSTRUCTION | No |

---

## Module Structure

```
weighment/
├── __init__.py
├── apps.py
├── models/
│   ├── __init__.py
│   └── weighment.py        # Weighment model
├── serializers.py          # WeighmentSerializer
├── views.py                # API views
├── urls.py                 # URL routing
├── admin.py                # Admin configuration
└── migrations/
```
