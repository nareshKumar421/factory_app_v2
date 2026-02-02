# Person Gate-In API Documentation

Base URL: `/api/v1/person-gatein/`

---

## Quick Reference

### Master APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/person-types/` | List/Create person types |
| GET/PUT/DELETE | `/person-types/{id}/` | Get/Update/Delete person type |
| GET/POST | `/gates/` | List/Create gates |
| GET/PUT/DELETE | `/gates/{id}/` | Get/Update/Delete gate |
| GET/POST | `/contractors/` | List/Create contractors |
| GET/PUT/DELETE | `/contractors/{id}/` | Get/Update/Delete contractor |
| GET/POST | `/visitors/` | List/Create visitors |
| GET/PUT/DELETE | `/visitors/{id}/` | Get/Update/Delete visitor |
| GET/POST | `/labours/` | List/Create labours |
| GET/PUT/DELETE | `/labours/{id}/` | Get/Update/Delete labour |

### Entry APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/entry/create/` | Create new entry (gate-in) |
| GET | `/entry/{id}/` | Get entry details with duration |
| POST | `/entry/{id}/exit/` | Mark entry as exited (gate-out) |
| POST | `/entry/{id}/cancel/` | Cancel an entry |
| PATCH | `/entry/{id}/update/` | Update entry details |
| GET | `/entry/inside/` | List all persons currently inside |
| GET | `/entries/` | Get entries with date filters |
| GET | `/entries/search/` | Search entries |

### History & Status APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/visitor/{id}/history/` | Get visitor entry history |
| GET | `/labour/{id}/history/` | Get labour entry history |
| GET | `/check-status/` | Check if person is inside |

### Dashboard API
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/` | Get dashboard statistics |

---

## Master APIs

### 1. Person Types

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/person-types/` | List all person types |
| POST | `/person-types/` | Create person type |
| GET | `/person-types/{id}/` | Get person type details |
| PUT | `/person-types/{id}/` | Update person type |
| DELETE | `/person-types/{id}/` | Delete person type |

**Payload (POST/PUT):**
```json
{
    "name": "Visitor",
    "is_active": true
}
```

**Response:**
```json
{
    "id": 1,
    "name": "Visitor",
    "is_active": true
}
```

---

### 2. Gates

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/gates/` | List all gates |
| POST | `/gates/` | Create gate |
| GET | `/gates/{id}/` | Get gate details |
| PUT | `/gates/{id}/` | Update gate |
| DELETE | `/gates/{id}/` | Delete gate |

**Payload (POST/PUT):**
```json
{
    "name": "Main Gate",
    "location": "North Entrance",
    "is_active": true
}
```

**Response:**
```json
{
    "id": 1,
    "name": "Main Gate",
    "location": "North Entrance",
    "is_active": true
}
```

---

### 3. Contractors

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/contractors/` | List all contractors |
| POST | `/contractors/` | Create contractor |
| GET | `/contractors/{id}/` | Get contractor details |
| PUT | `/contractors/{id}/` | Update contractor |
| DELETE | `/contractors/{id}/` | Delete contractor |

**Payload (POST/PUT):**
```json
{
    "contractor_name": "ABC Constructions",
    "contact_person": "John Doe",
    "mobile": "9876543210",
    "address": "123 Main Street, City",
    "contract_valid_till": "2026-12-31",
    "is_active": true
}
```

**Response:**
```json
{
    "id": 1,
    "contractor_name": "ABC Constructions",
    "contact_person": "John Doe",
    "mobile": "9876543210",
    "address": "123 Main Street, City",
    "contract_valid_till": "2026-12-31",
    "is_active": true
}
```

---

### 4. Visitors

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/visitors/` | List all visitors |
| POST | `/visitors/` | Create visitor |
| GET | `/visitors/{id}/` | Get visitor details |
| PUT | `/visitors/{id}/` | Update visitor |
| DELETE | `/visitors/{id}/` | Delete visitor |

**Payload (POST/PUT):**
```json
{
    "name": "Jane Smith",
    "mobile": "9876543210",
    "company_name": "XYZ Corp",
    "id_proof_type": "Aadhar",
    "id_proof_no": "1234-5678-9012",
    "photo": "<file>",
    "blacklisted": false
}
```

**Response:**
```json
{
    "id": 1,
    "name": "Jane Smith",
    "mobile": "9876543210",
    "company_name": "XYZ Corp",
    "id_proof_type": "Aadhar",
    "id_proof_no": "1234-5678-9012",
    "photo": "/media/visitor_photos/jane.jpg",
    "blacklisted": false,
    "created_at": "2026-01-30T10:00:00Z"
}
```

---

### 5. Labours

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/labours/` | List all labours |
| POST | `/labours/` | Create labour |
| GET | `/labours/{id}/` | Get labour details |
| PUT | `/labours/{id}/` | Update labour |
| DELETE | `/labours/{id}/` | Delete labour |

**Payload (POST/PUT):**
```json
{
    "name": "Ram Kumar",
    "contractor": 1,
    "mobile": "9876543210",
    "id_proof_no": "ABCD1234",
    "photo": "<file>",
    "skill_type": "Mason",
    "permit_valid_till": "2026-06-30",
    "is_active": true
}
```

**Response:**
```json
{
    "id": 1,
    "name": "Ram Kumar",
    "contractor": 1,
    "mobile": "9876543210",
    "id_proof_no": "ABCD1234",
    "photo": "/media/labour_photos/ram.jpg",
    "skill_type": "Mason",
    "permit_valid_till": "2026-06-30",
    "is_active": true
}
```

---

## Entry APIs

### 6. Create Entry (Gate-In)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/entry/create/` | Create new entry log |

**Payload for Visitor Entry:**
```json
{
    "person_type": 1,
    "visitor": 1,
    "gate_in": 1,
    "purpose": "Meeting with HR",
    "approved_by": 1,
    "vehicle_no": "UP32AB1234",
    "remarks": "Scheduled appointment"
}
```

**Payload for Labour Entry:**
```json
{
    "person_type": 2,
    "labour": 1,
    "gate_in": 1,
    "purpose": "Daily work",
    "vehicle_no": null,
    "remarks": null
}
```

**Response:**
```json
{
    "id": 1,
    "person_type": 1,
    "visitor": 1,
    "labour": null,
    "name_snapshot": "Jane Smith",
    "photo_snapshot": null,
    "gate_in": 1,
    "gate_out": null,
    "entry_time": "2026-01-30T09:00:00Z",
    "exit_time": null,
    "purpose": "Meeting with HR",
    "approved_by": 1,
    "vehicle_no": "UP32AB1234",
    "remarks": "Scheduled appointment",
    "status": "IN",
    "created_by": 1,
    "created_at": "2026-01-30T09:00:00Z",
    "updated_at": "2026-01-30T09:00:00Z"
}
```

**Error Response (Person already inside):**
```json
{
    "error": "Person already inside"
}
```

---

### 7. Exit Entry (Gate-Out)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/entry/{id}/exit/` | Mark entry as exited |

**Payload:**
```json
{
    "gate_out": 2
}
```

**Response:**
```json
{
    "id": 1,
    "person_type": 1,
    "visitor": 1,
    "labour": null,
    "name_snapshot": "Jane Smith",
    "photo_snapshot": null,
    "gate_in": 1,
    "gate_out": 2,
    "entry_time": "2026-01-30T09:00:00Z",
    "exit_time": "2026-01-30T17:30:00Z",
    "purpose": "Meeting with HR",
    "approved_by": 1,
    "vehicle_no": "UP32AB1234",
    "remarks": "Scheduled appointment",
    "status": "OUT",
    "created_by": 1,
    "created_at": "2026-01-30T09:00:00Z",
    "updated_at": "2026-01-30T17:30:00Z"
}
```

**Error Response (Already exited):**
```json
{
    "error": "Already exited"
}
```

---

### 8. Inside List (Currently Inside)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/entry/inside/` | List all persons currently inside |

**Response:**
```json
[
    {
        "id": 1,
        "person_type": 1,
        "visitor": 1,
        "labour": null,
        "name_snapshot": "Jane Smith",
        "gate_in": 1,
        "gate_out": null,
        "entry_time": "2026-01-30T09:00:00Z",
        "exit_time": null,
        "status": "IN"
    },
    {
        "id": 2,
        "person_type": 2,
        "visitor": null,
        "labour": 1,
        "name_snapshot": "Ram Kumar",
        "gate_in": 1,
        "gate_out": null,
        "entry_time": "2026-01-30T08:00:00Z",
        "exit_time": null,
        "status": "IN"
    }
]
```

---

### 9. Entries by Date (Filter Entries)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/entries/` | Get all entries with date and other filters |

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | string | No | Single date filter (YYYY-MM-DD) |
| `start_date` | string | No | Start date for range filter (YYYY-MM-DD) |
| `end_date` | string | No | End date for range filter (YYYY-MM-DD) |
| `status` | string | No | Filter by status: `IN`, `OUT`, `CANCELLED` |
| `person_type` | integer | No | Filter by person type ID |
| `gate_in` | integer | No | Filter by entry gate ID |
| `visitor` | integer | No | Filter by visitor ID |
| `labour` | integer | No | Filter by labour ID |

**Example Requests:**

```bash
# Get all entries for a specific date
GET /api/v1/person-gatein/entries/?date=2026-01-30

# Get entries for a date range
GET /api/v1/person-gatein/entries/?start_date=2026-01-01&end_date=2026-01-31

# Get entries for today that are still inside
GET /api/v1/person-gatein/entries/?date=2026-01-30&status=IN

# Get all visitor entries for a date range
GET /api/v1/person-gatein/entries/?start_date=2026-01-01&end_date=2026-01-31&person_type=1

# Get entries through a specific gate
GET /api/v1/person-gatein/entries/?date=2026-01-30&gate_in=1

# Get all entries for a specific visitor
GET /api/v1/person-gatein/entries/?visitor=1

# Get all entries for a specific labour
GET /api/v1/person-gatein/entries/?labour=1&start_date=2026-01-01

# Combine multiple filters
GET /api/v1/person-gatein/entries/?start_date=2026-01-01&end_date=2026-01-31&status=OUT&person_type=2&gate_in=1
```

**Response:**
```json
{
    "count": 2,
    "results": [
        {
            "id": 2,
            "person_type": 1,
            "visitor": 1,
            "labour": null,
            "name_snapshot": "Jane Smith",
            "photo_snapshot": null,
            "gate_in": 1,
            "gate_out": 2,
            "entry_time": "2026-01-30T14:00:00Z",
            "exit_time": "2026-01-30T18:00:00Z",
            "purpose": "Meeting",
            "approved_by": 1,
            "vehicle_no": "UP32AB1234",
            "remarks": null,
            "status": "OUT",
            "created_by": 1,
            "created_at": "2026-01-30T14:00:00Z",
            "updated_at": "2026-01-30T18:00:00Z"
        },
        {
            "id": 1,
            "person_type": 2,
            "visitor": null,
            "labour": 1,
            "name_snapshot": "Ram Kumar",
            "photo_snapshot": null,
            "gate_in": 1,
            "gate_out": null,
            "entry_time": "2026-01-30T08:00:00Z",
            "exit_time": null,
            "purpose": "Daily work",
            "approved_by": null,
            "vehicle_no": null,
            "remarks": null,
            "status": "IN",
            "created_by": 1,
            "created_at": "2026-01-30T08:00:00Z",
            "updated_at": "2026-01-30T08:00:00Z"
        }
    ]
}
```

**Error Response (Invalid date format):**
```json
{
    "error": "Invalid date format. Use YYYY-MM-DD"
}
```

**Notes:**
- Results are ordered by entry time (newest first)
- If no filters are provided, all entries are returned
- `date` parameter takes precedence for single day filtering
- Use `start_date` and `end_date` together for date range filtering
- All filters can be combined

---

### 10. Entry Detail

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/entry/{id}/` | Get detailed information about a specific entry |

**Response:**
```json
{
    "id": 1,
    "person_type": 1,
    "visitor": 1,
    "labour": null,
    "name_snapshot": "Jane Smith",
    "photo_snapshot": null,
    "gate_in": 1,
    "gate_out": 2,
    "entry_time": "2026-01-30T09:00:00Z",
    "exit_time": "2026-01-30T17:30:00Z",
    "purpose": "Meeting with HR",
    "approved_by": 1,
    "vehicle_no": "UP32AB1234",
    "remarks": "Scheduled appointment",
    "status": "OUT",
    "created_by": 1,
    "created_at": "2026-01-30T09:00:00Z",
    "updated_at": "2026-01-30T17:30:00Z",
    "duration": {
        "hours": 8,
        "minutes": 30,
        "seconds": 0,
        "total_minutes": 510,
        "formatted": "8h 30m"
    }
}
```

**Error Response (Entry not found):**
```json
{
    "error": "No EntryLog matches the given query."
}
```

---

### 11. Cancel Entry

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/entry/{id}/cancel/` | Cancel an entry (only for entries with status 'IN') |

**Payload:**
```json
{
    "reason": "Entered by mistake"
}
```

**Response:**
```json
{
    "id": 1,
    "person_type": 1,
    "visitor": 1,
    "labour": null,
    "name_snapshot": "Jane Smith",
    "status": "CANCELLED",
    "remarks": "Cancelled: Entered by mistake",
    ...
}
```

**Error Response:**
```json
{
    "error": "Only entries with status 'IN' can be cancelled"
}
```

---

### 12. Update Entry

| Method | Endpoint | Description |
|--------|----------|-------------|
| PATCH | `/entry/{id}/update/` | Update entry details |

**Payload (all fields optional):**
```json
{
    "purpose": "Updated meeting purpose",
    "remarks": "Additional notes",
    "vehicle_no": "UP32XY9999",
    "approved_by": 2
}
```

**Allowed Fields:**
- `purpose` - Purpose of visit
- `remarks` - Additional remarks
- `vehicle_no` - Vehicle number
- `approved_by` - ID of approving user

**Response:**
```json
{
    "id": 1,
    "person_type": 1,
    "visitor": 1,
    "purpose": "Updated meeting purpose",
    "remarks": "Additional notes",
    "vehicle_no": "UP32XY9999",
    "approved_by": 2,
    ...
}
```

---

### 13. Search Entries

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/entries/search/` | Search entries by name, vehicle, or purpose |

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query |
| `status` | string | No | Filter by status: `IN`, `OUT`, `CANCELLED` |

**Searchable Fields:**
- `name_snapshot` - Entry name
- `vehicle_no` - Vehicle number
- `purpose` - Purpose of visit
- `visitor.name` - Visitor name
- `visitor.mobile` - Visitor mobile
- `labour.name` - Labour name
- `labour.mobile` - Labour mobile

**Example Requests:**
```bash
# Search by name
GET /api/v1/person-gatein/entries/search/?q=John

# Search by vehicle number
GET /api/v1/person-gatein/entries/search/?q=UP32

# Search with status filter
GET /api/v1/person-gatein/entries/search/?q=meeting&status=IN
```

**Response:**
```json
{
    "query": "John",
    "count": 3,
    "results": [
        {
            "id": 5,
            "name_snapshot": "John Doe",
            "status": "IN",
            ...
        },
        ...
    ]
}
```

**Notes:**
- Maximum 50 results returned
- Case-insensitive search
- Results ordered by entry time (newest first)

---

### 14. Visitor Entry History

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/visitor/{visitor_id}/history/` | Get complete entry history for a visitor |

**Response:**
```json
{
    "visitor": {
        "id": 1,
        "name": "Jane Smith",
        "mobile": "9876543210",
        "company_name": "XYZ Corp",
        "id_proof_type": "Aadhar",
        "id_proof_no": "1234-5678-9012",
        "photo": "/media/visitor_photos/jane.jpg",
        "blacklisted": false,
        "created_at": "2026-01-15T10:00:00Z"
    },
    "is_inside": true,
    "current_entry": {
        "id": 10,
        "gate_in": 1,
        "entry_time": "2026-01-30T09:00:00Z",
        "status": "IN",
        ...
    },
    "total_visits": 5,
    "entries": [
        {
            "id": 10,
            "entry_time": "2026-01-30T09:00:00Z",
            "status": "IN",
            ...
        },
        {
            "id": 8,
            "entry_time": "2026-01-25T10:00:00Z",
            "exit_time": "2026-01-25T16:00:00Z",
            "status": "OUT",
            ...
        },
        ...
    ]
}
```

---

### 15. Labour Entry History

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/labour/{labour_id}/history/` | Get complete entry history for a labour |

**Response:**
```json
{
    "labour": {
        "id": 1,
        "name": "Ram Kumar",
        "contractor": 1,
        "mobile": "9876543210",
        "id_proof_no": "ABCD1234",
        "photo": "/media/labour_photos/ram.jpg",
        "skill_type": "Mason",
        "permit_valid_till": "2026-06-30",
        "is_active": true
    },
    "is_inside": false,
    "current_entry": null,
    "total_entries": 25,
    "entries": [
        {
            "id": 45,
            "entry_time": "2026-01-29T08:00:00Z",
            "exit_time": "2026-01-29T17:00:00Z",
            "status": "OUT",
            ...
        },
        ...
    ]
}
```

---

### 16. Check Person Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/check-status/` | Check if a visitor or labour is currently inside |

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `visitor` | integer | No* | Visitor ID to check |
| `labour` | integer | No* | Labour ID to check |

*Either `visitor` or `labour` is required.

**Example Requests:**
```bash
# Check visitor status
GET /api/v1/person-gatein/check-status/?visitor=1

# Check labour status
GET /api/v1/person-gatein/check-status/?labour=1
```

**Response (Visitor):**
```json
{
    "person_type": "visitor",
    "person_id": 1,
    "name": "Jane Smith",
    "is_inside": true,
    "current_entry": {
        "id": 10,
        "gate_in": 1,
        "entry_time": "2026-01-30T09:00:00Z",
        "status": "IN",
        ...
    },
    "blacklisted": false
}
```

**Response (Labour):**
```json
{
    "person_type": "labour",
    "person_id": 1,
    "name": "Ram Kumar",
    "is_inside": false,
    "current_entry": null,
    "is_active": true,
    "permit_valid": true,
    "permit_valid_till": "2026-06-30"
}
```

**Notes:**
- For visitors: includes `blacklisted` status
- For labours: includes `is_active`, `permit_valid`, and `permit_valid_till`

---

### 17. Dashboard Statistics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/` | Get dashboard statistics for gate-in management |

**Response:**
```json
{
    "current": {
        "total_inside": 45,
        "visitors_inside": 12,
        "labours_inside": 33,
        "long_duration_count": 3
    },
    "today": {
        "total_entries": 78,
        "visitors": 25,
        "labours": 53,
        "exits": 33
    },
    "gate_wise": [
        {
            "id": 1,
            "name": "Main Gate",
            "inside_count": 30
        },
        {
            "id": 2,
            "name": "Back Gate",
            "inside_count": 15
        }
    ],
    "person_type_wise": [
        {
            "id": 1,
            "name": "Visitor",
            "inside_count": 12,
            "today_count": 25
        },
        {
            "id": 2,
            "name": "Labour",
            "inside_count": 33,
            "today_count": 53
        }
    ],
    "recent_entries": [
        {
            "id": 100,
            "name_snapshot": "John Doe",
            "entry_time": "2026-01-30T14:30:00Z",
            "status": "IN",
            ...
        },
        ...
    ]
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `current.total_inside` | Total persons currently inside |
| `current.visitors_inside` | Visitors currently inside |
| `current.labours_inside` | Labours currently inside |
| `current.long_duration_count` | Entries exceeding 8 hours |
| `today.total_entries` | Total entries today |
| `today.visitors` | Visitor entries today |
| `today.labours` | Labour entries today |
| `today.exits` | Total exits today |
| `gate_wise` | Inside count per gate |
| `person_type_wise` | Count per person type |
| `recent_entries` | Last 10 entries |

---

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request / Validation Error |
| 401 | Unauthorized (JWT token required) |
| 404 | Not Found |
| 500 | Server Error |

---

## Authentication

All endpoints require JWT authentication.

**Header:**
```
Authorization: Bearer <access_token>
```

---

## Entry Status Values

| Status | Description |
|--------|-------------|
| IN | Person is currently inside |
| OUT | Person has exited |
| CANCELLED | Entry was cancelled |

---

## Models Reference

### PersonType
- `name` (string, unique): Visitor / Labour
- `is_active` (boolean)

### Gate
- `name` (string): Gate name
- `location` (string, optional): Gate location
- `is_active` (boolean)

### Contractor
- `contractor_name` (string)
- `contact_person` (string, optional)
- `mobile` (string, optional)
- `address` (text, optional)
- `contract_valid_till` (date, optional)
- `is_active` (boolean)

### Visitor
- `name` (string)
- `mobile` (string, optional)
- `company_name` (string, optional)
- `id_proof_type` (string, optional)
- `id_proof_no` (string, optional)
- `photo` (image, optional)
- `blacklisted` (boolean)
- `created_at` (datetime, auto)

### Labour
- `name` (string)
- `contractor` (FK to Contractor)
- `mobile` (string, optional)
- `id_proof_no` (string, optional)
- `photo` (image, optional)
- `skill_type` (string, optional)
- `permit_valid_till` (date, optional)
- `is_active` (boolean)

### EntryLog
- `person_type` (FK to PersonType)
- `visitor` (FK to Visitor, optional)
- `labour` (FK to Labour, optional)
- `name_snapshot` (string): Captured name at entry time
- `photo_snapshot` (image, optional)
- `gate_in` (FK to Gate)
- `gate_out` (FK to Gate, optional)
- `entry_time` (datetime, auto)
- `exit_time` (datetime, optional)
- `purpose` (string, optional)
- `approved_by` (FK to User, optional)
- `vehicle_no` (string, optional)
- `remarks` (text, optional)
- `status` (string): IN / OUT / CANCELLED
- `created_by` (FK to User)
- `created_at` (datetime, auto)
- `updated_at` (datetime, auto)
