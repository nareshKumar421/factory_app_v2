# Vehicle Management Module

## Overview

The **Vehicle Management Module** handles transporters, vehicles, and vehicle entry (gate entry) management. It serves as the foundation for tracking vehicles entering the factory premises.

---

## Models

### Transporter

| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField(150) | Unique transporter name |
| `contact_person` | CharField(100) | Contact person name |
| `mobile_no` | CharField(15) | Contact mobile number |
| `created_at` | DateTimeField | Auto-generated |
| `created_by` | ForeignKey | User who created |

### Vehicle

| Field | Type | Description |
|-------|------|-------------|
| `vehicle_number` | CharField(20) | Unique vehicle registration number |
| `vehicle_type` | CharField(20) | TRUCK/TEMPO/CONTAINER/TRACTOR |
| `transporter` | ForeignKey | Link to Transporter |
| `capacity_ton` | DecimalField | Vehicle capacity in tons |
| `created_at` | DateTimeField | Auto-generated |
| `created_by` | ForeignKey | User who created |

**Vehicle Types:**
- TRUCK
- TEMPO
- CONTAINER
- TRACTOR

---

## API Documentation

### Base URL
```
/api/v1/vehicle-management/
```

### Headers Required
```
Authorization: Bearer <access_token>
Company-Code: <company_code>
```

---

## Transporter APIs

### 1. List/Create Transporters

```
GET /api/v1/vehicle-management/transporters/
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "ABC Transport",
        "contact_person": "John Doe",
        "mobile_no": "9876543210",
        "created_at": "2026-01-01T10:00:00Z"
    }
]
```

```
POST /api/v1/vehicle-management/transporters/
```

**Request Body:**
```json
{
    "name": "ABC Transport",
    "contact_person": "John Doe",
    "mobile_no": "9876543210"
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "name": "ABC Transport",
    "contact_person": "John Doe",
    "mobile_no": "9876543210",
    "created_at": "2026-01-01T10:00:00Z"
}
```

---

### 2. Get Transporter Names (Dropdown)

```
GET /api/v1/vehicle-management/transporters/names/
```

**Response (200 OK):**
```json
[
    {"id": 1, "name": "ABC Transport"},
    {"id": 2, "name": "XYZ Logistics"}
]
```

---

### 3. Get Transporter Details

```
GET /api/v1/vehicle-management/transporters/{id}/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "ABC Transport",
    "contact_person": "John Doe",
    "mobile_no": "9876543210",
    "created_at": "2026-01-01T10:00:00Z"
}
```

---

### 4. Update Transporter

```
PUT /api/v1/vehicle-management/transporters/{id}/
```

**Request Body:**
```json
{
    "name": "ABC Transport Updated",
    "contact_person": "Jane Doe",
    "mobile_no": "9876543211"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "ABC Transport Updated",
    "contact_person": "Jane Doe",
    "mobile_no": "9876543211",
    "created_at": "2026-01-01T10:00:00Z"
}
```

---

## Vehicle APIs

### 4. List/Create Vehicles

```
GET /api/v1/vehicle-management/vehicles/
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "vehicle_number": "MP09AB1234",
        "vehicle_type": "TRUCK",
        "transporter": {
            "id": 1,
            "name": "ABC Transport",
            "contact_person": "John Doe",
            "mobile_no": "9876543210",
            "created_at": "2026-01-01T10:00:00Z"
        },
        "capacity_ton": "10.00",
        "created_at": "2026-01-01T10:00:00Z"
    }
]
```

```
POST /api/v1/vehicle-management/vehicles/
```

**Request Body:**
```json
{
    "vehicle_number": "MP09AB1234",
    "vehicle_type": "TRUCK",
    "transporter": 1,
    "capacity_ton": 10.00
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "vehicle_number": "MP09AB1234",
    "vehicle_type": "TRUCK",
    "transporter": {
        "id": 1,
        "name": "ABC Transport",
        "contact_person": "John Doe",
        "mobile_no": "9876543210",
        "created_at": "2026-01-01T10:00:00Z"
    },
    "capacity_ton": "10.00",
    "created_at": "2026-01-01T10:00:00Z"
}
```

---

### 5. Get Vehicle Names (Dropdown)

```
GET /api/v1/vehicle-management/vehicles/names/
```

**Response (200 OK):**
```json
[
    {"id": 1, "vehicle_number": "MP09AB1234"},
    {"id": 2, "vehicle_number": "MP09CD5678"}
]
```

---

### 6. Get Vehicle Details

```
GET /api/v1/vehicle-management/vehicles/{id}/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "vehicle_number": "MP09AB1234",
    "vehicle_type": "TRUCK",
    "transporter": {
        "id": 1,
        "name": "ABC Transport",
        "contact_person": "John Doe",
        "mobile_no": "9876543210",
        "created_at": "2026-01-01T10:00:00Z"
    },
    "capacity_ton": "10.00",
    "created_at": "2026-01-01T10:00:00Z"
}
```

---

## Vehicle Entry APIs

### 7. List/Create Vehicle Entries

```
GET /api/v1/vehicle-management/vehicle-entries/?entry_type=RAW_MATERIAL&from_date=2026-01-01&to_date=2026-01-31
```

**Query Parameters (Required):**
- `entry_type`: RAW_MATERIAL | DAILY_NEED | MAINTENANCE | CONSTRUCTION
- `from_date`: YYYY-MM-DD
- `to_date`: YYYY-MM-DD

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "entry_no": "GE-2026-001",
        "company": {"id": 1, "name": "JIVO OIL", "code": "JIVO_OIL"},
        "vehicle": {
            "id": 1,
            "vehicle_number": "MP09AB1234",
            "vehicle_type": "TRUCK",
            "transporter": {...},
            "capacity_ton": "10.00"
        },
        "driver": {
            "id": 1,
            "name": "Ramesh Kumar",
            "mobile_no": "9876543210",
            "license_no": "MP0920210012345"
        },
        "status": "DRAFT",
        "entry_time": "2026-01-15T10:00:00Z",
        "entry_type": "RAW_MATERIAL",
        "remarks": ""
    }
]
```

```
POST /api/v1/vehicle-management/vehicle-entries/
```

**Request Body:**
```json
{
    "vehicle": 1,
    "driver": 1,
    "entry_type": "RAW_MATERIAL",
    "remarks": "Scheduled delivery"
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "entry_no": "GE-2026-001",
    "status": "DRAFT"
}
```

---

### 8. Get Vehicle Entry Details

```
GET /api/v1/vehicle-management/vehicle-entries/{id}/
```

---

### 9. Get Vehicle Entry Count

```
GET /api/v1/vehicle-management/vehicle-entries/count/?entry_type=RAW_MATERIAL&from_date=2026-01-01&to_date=2026-01-31
```

**Response (200 OK):**
```json
{
    "total_vehicle_entries": [
        {"status": "DRAFT", "count": 5},
        {"status": "IN_PROGRESS", "count": 3},
        {"status": "COMPLETED", "count": 10}
    ]
}
```

---

### 10. List Vehicle Entries by Status

```
GET /api/v1/vehicle-management/vehicle-entries/list-by-status/?status=IN_PROGRESS&entry_type=RAW_MATERIAL&from_date=2026-01-01&to_date=2026-01-31
```

---

## Module Structure

```
vehicle_management/
├── __init__.py
├── apps.py
├── models/
│   ├── __init__.py
│   ├── transporter.py      # Transporter model
│   └── vehicle.py          # Vehicle model
├── serializers.py          # All serializers
├── views.py                # API views
├── urls.py                 # URL routing
├── admin.py                # Admin configuration
└── migrations/
```
