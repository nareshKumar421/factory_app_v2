# Driver Management Module

## Overview

The **Driver Management Module** handles driver registration and the core **VehicleEntry** model that serves as the foundation for all gate entry types (Raw Material, Daily Need, Maintenance, Construction).

---

## Models

### Driver

| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField(100) | Driver's full name |
| `mobile_no` | CharField(15) | Mobile number |
| `license_no` | CharField(50) | Unique driving license number |
| `id_proof_type` | CharField(50) | Type of ID proof (Aadhar, PAN, etc.) |
| `id_proof_number` | CharField(50) | ID proof number |
| `photo` | ImageField | Driver's photo |
| `created_at` | DateTimeField | Auto-generated |
| `created_by` | ForeignKey | User who created |

### VehicleEntry (Core Gate Entry Model)

| Field | Type | Description |
|-------|------|-------------|
| `entry_no` | CharField(30) | Unique entry number (auto-generated) |
| `company` | ForeignKey | Link to Company |
| `vehicle` | ForeignKey | Link to Vehicle |
| `driver` | ForeignKey | Link to Driver |
| `entry_type` | CharField(20) | Type of entry |
| `status` | CharField(20) | Entry status |
| `is_locked` | BooleanField | Lock status |
| `entry_time` | DateTimeField | Entry timestamp |
| `remarks` | TextField | Additional remarks |
| `created_at` | DateTimeField | Auto-generated |
| `created_by` | ForeignKey | User who created |

**Entry Types:**
| Code | Display |
|------|---------|
| `RAW_MATERIAL` | Raw Material |
| `DAILY_NEED` | Daily Need / Canteen |
| `MAINTENANCE` | Maintenance |
| `CONSTRUCTION` | Construction |

**Status Flow:**
| Code | Display |
|------|---------|
| `DRAFT` | Draft |
| `IN_PROGRESS` | In Progress |
| `QC_PENDING` | QC Pending |
| `QC_COMPLETED` | QC Completed |
| `COMPLETED` | Completed |
| `CANCELLED` | Cancelled |

---

## API Documentation

### Base URL
```
/api/v1/driver-management/
```

### Headers Required
```
Authorization: Bearer <access_token>
```

---

### 1. List/Create Drivers

```
GET /api/v1/driver-management/drivers/
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Ramesh Kumar",
        "mobile_no": "9876543210",
        "license_no": "MP0920210012345",
        "id_proof_type": "Aadhar",
        "id_proof_number": "1234-5678-9012",
        "photo": "/media/drivers/photos/ramesh.jpg",
        "created_at": "2026-01-01T10:00:00Z"
    }
]
```

```
POST /api/v1/driver-management/drivers/
```

**Request Body:**
```json
{
    "name": "Ramesh Kumar",
    "mobile_no": "9876543210",
    "license_no": "MP0920210012345",
    "id_proof_type": "Aadhar",
    "id_proof_number": "1234-5678-9012"
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "name": "Ramesh Kumar",
    "mobile_no": "9876543210",
    "license_no": "MP0920210012345",
    "id_proof_type": "Aadhar",
    "id_proof_number": "1234-5678-9012",
    "photo": null,
    "created_at": "2026-01-01T10:00:00Z"
}
```

---

### 2. Get/Update Driver Details

```
GET /api/v1/driver-management/drivers/{id}/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "Ramesh Kumar",
    "mobile_no": "9876543210",
    "license_no": "MP0920210012345",
    "id_proof_type": "Aadhar",
    "id_proof_number": "1234-5678-9012",
    "photo": "/media/drivers/photos/ramesh.jpg",
    "created_at": "2026-01-01T10:00:00Z"
}
```

```
PUT /api/v1/driver-management/drivers/{id}/
```

**Request Body (Partial Update):**
```json
{
    "mobile_no": "9876543211"
}
```

---

### 3. Get Driver Names (Dropdown)

```
GET /api/v1/driver-management/drivers/names/
```

**Response (200 OK):**
```json
[
    {"id": 1, "name": "Ramesh Kumar"},
    {"id": 2, "name": "Suresh Singh"}
]
```

---

## Gate Entry Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         GATE ENTRY FLOW                                   │
└──────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │    DRAFT     │ ──► Vehicle Entry created
    └──────┬───────┘     entry_no generated
           │
           ▼
    ┌──────────────┐
    │ IN_PROGRESS  │ ──► Security check started
    └──────┬───────┘
           │
           ├─────────────────────────────────────┐
           │                                     │
           ▼                                     ▼
    ┌──────────────┐                    ┌──────────────┐
    │  QC_PENDING  │ (Raw Material)     │  COMPLETED   │ (Daily Need/
    └──────┬───────┘                    └──────────────┘  Maintenance/
           │                                              Construction)
           ▼
    ┌──────────────┐
    │ QC_COMPLETED │ ──► All QC inspections done
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  COMPLETED   │ ──► Entry locked (is_locked=True)
    └──────────────┘
```

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `vehicle_management` | Vehicle and Transporter data |
| `security_checks` | Security inspection (OneToOne) |
| `raw_material_gatein` | PO receipts (ForeignKey) |
| `weighment` | Weight measurement (OneToOne) |
| `quality_control` | QC inspection (via PO items) |
| `daily_needs_gatein` | Daily need entry (OneToOne) |
| `maintenance_gatein` | Maintenance entry (OneToOne) |
| `construction_gatein` | Construction entry (OneToOne) |

---

## Module Structure

```
driver_management/
├── __init__.py
├── apps.py
├── models/
│   ├── __init__.py
│   ├── driver.py           # Driver model
│   └── vehicle_entry.py    # VehicleEntry model
├── serializers.py          # Driver serializers
├── views.py                # API views
├── urls.py                 # URL routing
├── admin.py                # Admin configuration
└── migrations/
```
