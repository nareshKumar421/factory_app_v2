# Quality Control API Documentation

## Base URL
```
/api/v1/quality-control/
```

## Headers Required
```
Authorization: Bearer <access_token>
Company-Code: <company_code>
```

---

## Material Type APIs

### 1. List Material Types

List all active material types for the company.

```
GET /api/v1/quality-control/material-types/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.can_manage_material_types`

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Soybean Oil",
        "description": "Crude soybean oil",
        "is_active": true
    }
]
```

---

### 2. Create Material Type

```
POST /api/v1/quality-control/material-types/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.can_manage_material_types`

**Request Body:**
```json
{
    "name": "Soybean Oil",
    "description": "Crude soybean oil"
}
```

**Response (201 Created):** Returns created material type data.

---

### 3. Get Material Type Detail

```
GET /api/v1/quality-control/material-types/{material_type_id}/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.can_manage_material_types`

---

### 4. Update Material Type

```
PUT /api/v1/quality-control/material-types/{material_type_id}/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.can_manage_material_types`

---

### 5. Delete Material Type (Soft Delete)

```
DELETE /api/v1/quality-control/material-types/{material_type_id}/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.can_manage_material_types`

**Response:** `204 No Content`

---

## QC Parameter Master APIs

### 6. List QC Parameters for Material Type

```
GET /api/v1/quality-control/material-types/{material_type_id}/parameters/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.can_manage_qc_parameters`

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "parameter_name": "Moisture Content",
        "standard_value": "< 0.5%",
        "is_mandatory": true,
        "is_active": true
    }
]
```

---

### 7. Create QC Parameter

```
POST /api/v1/quality-control/material-types/{material_type_id}/parameters/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.can_manage_qc_parameters`

---

### 8. Get QC Parameter Detail

```
GET /api/v1/quality-control/parameters/{parameter_id}/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.can_manage_qc_parameters`

---

### 9. Update QC Parameter

```
PUT /api/v1/quality-control/parameters/{parameter_id}/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.can_manage_qc_parameters`

---

### 10. Delete QC Parameter (Soft Delete)

```
DELETE /api/v1/quality-control/parameters/{parameter_id}/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.can_manage_qc_parameters`

**Response:** `204 No Content`

---

## Material Arrival Slip APIs

### 11. List Arrival Slips

List all arrival slips for the company. Supports filtering by status.

```
GET /api/v1/quality-control/arrival-slips/
GET /api/v1/quality-control/arrival-slips/?status=SUBMITTED
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.view_materialarrivalslip`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by status (DRAFT, SUBMITTED, REJECTED) |

---

### 12. Get/Create Arrival Slip for PO Item

**GET** - Retrieve existing arrival slip for a PO item.
**POST** - Create or update arrival slip for a PO item.

```
GET /api/v1/quality-control/po-items/{po_item_id}/arrival-slip/
POST /api/v1/quality-control/po-items/{po_item_id}/arrival-slip/
```

**Permission Required (GET/POST):** `IsAuthenticated` + `HasCompanyContext` + (`quality_control.add_materialarrivalslip` or `quality_control.change_materialarrivalslip`) for POST, `quality_control.view_materialarrivalslip` for GET

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Arrival slip already submitted` |
| 404 | `Arrival slip not found` |

---

### 13. Get Arrival Slip Detail

```
GET /api/v1/quality-control/arrival-slips/{slip_id}/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.view_materialarrivalslip`

---

### 14. Submit Arrival Slip to QA

```
POST /api/v1/quality-control/arrival-slips/{slip_id}/submit/
```

**Content-Type:** `multipart/form-data`

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.can_submit_arrival_slip`

**Form Fields (files):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `certificate_of_analysis` | file | Conditional | Required if `has_certificate_of_analysis` is `true` on the arrival slip |
| `certificate_of_quantity` | file | Conditional | Required if `has_certificate_of_quantity` is `true` on the arrival slip |

Both attachments are optional by default. They become required only when the corresponding boolean flag was set to `true` during arrival slip creation/update. Any file format is accepted.

On resubmission (after rejection), existing attachments of the same type are replaced.

**Response (200 OK):** Returns updated arrival slip data including `attachments` array.

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Already submitted` |
| 400 | `Certificate of Analysis attachment is required when has_certificate_of_analysis is true.` |
| 400 | `Certificate of Quantity attachment is required when has_certificate_of_quantity is true.` |

---

## Raw Material Inspection APIs

### 15. List Pending Inspections

List submitted arrival slips pending QA inspection.

```
GET /api/v1/quality-control/inspections/pending/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.view_rawmaterialinspection`

---

### 16. Get/Create Inspection for Arrival Slip

**GET** - Retrieve existing inspection for an arrival slip.
**POST** - Create or update inspection for an arrival slip.

```
GET /api/v1/quality-control/arrival-slips/{slip_id}/inspection/
POST /api/v1/quality-control/arrival-slips/{slip_id}/inspection/
```

**Permission Required (GET/POST):** `IsAuthenticated` + `HasCompanyContext` + (`quality_control.add_rawmaterialinspection` or `quality_control.change_rawmaterialinspection`) for POST, `quality_control.view_rawmaterialinspection` for GET

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Arrival slip must be submitted first` |
| 400 | `Inspection is locked` |

---

### 17. Get Inspection Detail

```
GET /api/v1/quality-control/inspections/{inspection_id}/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.view_rawmaterialinspection`

---

### 18. Get/Update Parameter Results

**GET** - List parameter results for an inspection.
**POST** - Bulk update parameter results.

```
GET /api/v1/quality-control/inspections/{inspection_id}/parameters/
POST /api/v1/quality-control/inspections/{inspection_id}/parameters/
```

**Permission Required (GET/POST):** `IsAuthenticated` + `HasCompanyContext` + (`quality_control.add_rawmaterialinspection` or `quality_control.change_rawmaterialinspection`) for POST, `quality_control.view_rawmaterialinspection` for GET

**Request Body (POST):**
```json
{
    "results": [
        {
            "parameter_master_id": 1,
            "result_value": "0.3%",
            "parameter_name": "Moisture Content",
            "standard_value": "< 0.5%"
        }
    ]
}
```

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Inspection is locked` |

---

### 19. Submit Inspection for Approval

Submit inspection for QA Chemist approval.

```
POST /api/v1/quality-control/inspections/{inspection_id}/submit/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.can_submit_inspection`

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Inspection is locked` |
| 400 | `Already submitted` |
| 400 | `All mandatory parameters must have results` |

---

## Approval APIs

### 20. QA Chemist Approval

```
POST /api/v1/quality-control/inspections/{inspection_id}/approve/chemist/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.can_approve_as_chemist`

**Request Body:**
```json
{
    "remarks": "Parameters within acceptable range"
}
```

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Inspection is locked` |
| 400 | `Inspection must be submitted first` |

---

### 21. QA Manager Approval

```
POST /api/v1/quality-control/inspections/{inspection_id}/approve/qam/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.can_approve_as_qam`

**Request Body:**
```json
{
    "remarks": "Approved for use",
    "final_status": "ACCEPTED"
}
```

**Notes:**
- `final_status` can be: `ACCEPTED`, `REJECTED`, `HOLD`
- QA Chemist must approve first

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Inspection is locked` |
| 400 | `QA Chemist must approve first` |

---

### 22. Reject Inspection

Reject inspection - sends back to security guard.

```
POST /api/v1/quality-control/inspections/{inspection_id}/reject/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `quality_control.can_reject_inspection`

**Request Body:**
```json
{
    "remarks": "Sample contaminated, re-inspection needed"
}
```

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Inspection is locked` |

---

## Permission Summary

| Endpoint | Method | Permission Codename |
|----------|--------|---------------------|
| `/material-types/` | GET/POST | `can_manage_material_types` |
| `/material-types/{id}/` | GET/PUT/DELETE | `can_manage_material_types` |
| `/material-types/{id}/parameters/` | GET/POST | `can_manage_qc_parameters` |
| `/parameters/{id}/` | GET/PUT/DELETE | `can_manage_qc_parameters` |
| `/arrival-slips/` | GET | `view_materialarrivalslip` |
| `/po-items/{id}/arrival-slip/` | GET | `view_materialarrivalslip` |
| `/po-items/{id}/arrival-slip/` | POST | `add_materialarrivalslip` or `change_materialarrivalslip` |
| `/arrival-slips/{id}/` | GET | `view_materialarrivalslip` |
| `/arrival-slips/{id}/submit/` | POST | `can_submit_arrival_slip` |
| `/inspections/pending/` | GET | `view_rawmaterialinspection` |
| `/arrival-slips/{id}/inspection/` | GET | `view_rawmaterialinspection` |
| `/arrival-slips/{id}/inspection/` | POST | `add_rawmaterialinspection` or `change_rawmaterialinspection` |
| `/inspections/{id}/` | GET | `view_rawmaterialinspection` |
| `/inspections/{id}/parameters/` | GET | `view_rawmaterialinspection` |
| `/inspections/{id}/parameters/` | POST | `add_rawmaterialinspection` or `change_rawmaterialinspection` |
| `/inspections/{id}/submit/` | POST | `can_submit_inspection` |
| `/inspections/{id}/approve/chemist/` | POST | `can_approve_as_chemist` |
| `/inspections/{id}/approve/qam/` | POST | `can_approve_as_qam` |
| `/inspections/{id}/reject/` | POST | `can_reject_inspection` |

## All Permissions

| Permission Codename | Description |
|---------------------|-------------|
| `quality_control.add_materialarrivalslip` | Can add material arrival slip |
| `quality_control.view_materialarrivalslip` | Can view material arrival slip |
| `quality_control.change_materialarrivalslip` | Can change material arrival slip |
| `quality_control.delete_materialarrivalslip` | Can delete material arrival slip |
| `quality_control.can_submit_arrival_slip` | Can submit arrival slip to QA |
| `quality_control.add_rawmaterialinspection` | Can add raw material inspection |
| `quality_control.view_rawmaterialinspection` | Can view raw material inspection |
| `quality_control.change_rawmaterialinspection` | Can change raw material inspection |
| `quality_control.delete_rawmaterialinspection` | Can delete raw material inspection |
| `quality_control.can_submit_inspection` | Can submit inspection for approval |
| `quality_control.can_approve_as_chemist` | Can approve inspection as QA Chemist |
| `quality_control.can_approve_as_qam` | Can approve inspection as QA Manager |
| `quality_control.can_reject_inspection` | Can reject inspection |
| `quality_control.can_manage_material_types` | Can manage material types |
| `quality_control.can_manage_qc_parameters` | Can manage QC parameters |

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
    "detail": "Not found."
}
```
