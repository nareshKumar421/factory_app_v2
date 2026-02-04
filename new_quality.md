# New Quality Control Workflow

## Overview

This document describes the redesigned quality control workflow that properly separates responsibilities between Security Guard and QA/Lab personnel, with support for dynamic QC parameters per material type.

---

## Key Decisions

| Decision | Choice |
|----------|--------|
| Rejection flow | Send back to Security Guard to update arrival slip |
| QAM approval | Each item approved individually (not entire gate entry) |
| Arrival Slip | One per PO item (not per vehicle entry) |
| Inspection | One per arrival slip (linked to arrival slip, not directly to PO item) |

---

## Data Flow

```
POItemReceipt
      ↓ (OneToOne)
MaterialArrivalSlip (Security Guard fills)
      ↓ (OneToOne)
RawMaterialInspection (QA fills)
      ↓ (ForeignKey)
InspectionParameterResult (Dynamic parameters)
```

---

## Workflow

```
1. Security Guard creates Arrival Slip for each PO item
2. Security Guard submits Arrival Slip to QA
3. QA creates Inspection linked to Arrival Slip
4. QA fills dynamic parameters based on Material Type
5. QA Technician submits for approval
6. QA Chemist approves
7. QA Manager approves (each item individually)
8. Gate entry completed when all items approved
```

---

## New Models

### 1. MaterialArrivalSlip (Security Guard fills)

**File:** `quality_control/models/material_arrival_slip.py`

| Field | Type | Description |
|-------|------|-------------|
| po_item_receipt | OneToOne | Link to POItemReceipt |
| particulars | TextField | Item description |
| arrival_datetime | DateTimeField | Arrival date/time |
| weighing_required | BooleanField | Yes/No |
| party_name | CharField | Supplier name |
| billing_qty | DecimalField | Billing quantity |
| billing_uom | CharField | Unit of measurement |
| in_time_to_qa | DateTimeField | Time sent to QA |
| truck_no_as_per_bill | CharField | Truck number |
| commercial_invoice_no | CharField | Invoice number |
| eway_bill_no | CharField | E-way bill number |
| bilty_no | CharField | Bilty number |
| has_certificate_of_analysis | BooleanField | COA present |
| has_certificate_of_quantity | BooleanField | COQ present |
| status | CharField | DRAFT, SUBMITTED, REJECTED |
| is_submitted | BooleanField | Submitted to QA |
| submitted_at | DateTimeField | Submission timestamp |

### 2. MaterialType (Master Data)

**File:** `quality_control/models/material_type.py`

| Field | Type | Description |
|-------|------|-------------|
| code | CharField | Unique material type code |
| name | CharField | Material type name |
| description | TextField | Description |
| company | ForeignKey | Link to Company |

### 3. QCParameterMaster (Dynamic Parameters Definition)

**File:** `quality_control/models/qc_parameter_master.py`

| Field | Type | Description |
|-------|------|-------------|
| material_type | ForeignKey | Link to MaterialType |
| parameter_name | CharField | e.g., "Weight", "Colour", "Total Height" |
| parameter_code | CharField | Unique code |
| standard_value | CharField | e.g., "1.35±0.10", "Blue" |
| parameter_type | CharField | NUMERIC, TEXT, BOOLEAN, RANGE |
| min_value | DecimalField | For numeric validation |
| max_value | DecimalField | For numeric validation |
| uom | CharField | Unit of measurement |
| sequence | Integer | Display order |
| is_mandatory | BooleanField | Required field |

### 4. RawMaterialInspection (QA/Lab fills)

**File:** `quality_control/models/raw_material_inspection.py`

| Field | Type | Description |
|-------|------|-------------|
| arrival_slip | OneToOne | Link to MaterialArrivalSlip |
| report_no | CharField | Auto-generated report number |
| internal_lot_no | CharField | Auto-generated lot number |
| inspection_date | DateField | Inspection date |
| description_of_material | TextField | Material description |
| sap_code | CharField | SAP code |
| supplier_name | CharField | Supplier |
| manufacturer_name | CharField | Manufacturer |
| supplier_batch_lot_no | CharField | Supplier batch/lot |
| unit_packing | CharField | Unit packing info |
| purchase_order_no | CharField | PO number |
| invoice_bill_no | CharField | Invoice/Bill number |
| material_type | ForeignKey | Link to MaterialType |
| final_status | CharField | PENDING, ACCEPTED, REJECTED, HOLD |
| qa_chemist | ForeignKey | QA Chemist user |
| qa_chemist_approved_at | DateTimeField | Chemist approval time |
| qam | ForeignKey | QA Manager user |
| qam_approved_at | DateTimeField | QAM approval time |
| workflow_status | CharField | DRAFT, SUBMITTED, QA_CHEMIST_APPROVED, QAM_APPROVED |
| is_locked | BooleanField | Lock after completion |

### 5. InspectionParameterResult (Dynamic Parameter Results)

**File:** `quality_control/models/inspection_parameter_result.py`

| Field | Type | Description |
|-------|------|-------------|
| inspection | ForeignKey | Link to RawMaterialInspection |
| parameter_master | ForeignKey | Link to QCParameterMaster |
| parameter_name | CharField | Parameter name (copied) |
| standard_value | CharField | Standard value (copied) |
| result_value | CharField | Actual test result |
| result_numeric | DecimalField | Numeric result (if applicable) |
| is_within_spec | BooleanField | Pass/Fail for this parameter |
| remarks | TextField | Optional remarks |

---

## Enums

**File:** `quality_control/enums.py`

```python
class ArrivalSlipStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SUBMITTED = "SUBMITTED", "Submitted to QA"
    REJECTED = "REJECTED", "Rejected by QA"

class InspectionStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"
    HOLD = "HOLD", "On Hold"

class InspectionWorkflowStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SUBMITTED = "SUBMITTED", "Submitted"
    QA_CHEMIST_APPROVED = "QA_CHEMIST_APPROVED", "QA Chemist Approved"
    QAM_APPROVED = "QAM_APPROVED", "QAM Approved"
    COMPLETED = "COMPLETED", "Completed"
```

---

## API Endpoints

### Arrival Slip APIs (Security Guard)
```
GET  /api/v1/quality-control/arrival-slips/                    # List all arrival slips
GET  /api/v1/quality-control/po-items/{id}/arrival-slip/       # Get arrival slip for PO item
POST /api/v1/quality-control/po-items/{id}/arrival-slip/       # Create/update arrival slip
GET  /api/v1/quality-control/arrival-slips/{id}/               # Get arrival slip by ID
POST /api/v1/quality-control/arrival-slips/{id}/submit/        # Submit to QA
```

### Inspection APIs (QA/Lab)
```
GET  /api/v1/quality-control/inspections/pending/              # List pending arrival slips for QA
GET  /api/v1/quality-control/arrival-slips/{id}/inspection/    # Get inspection for arrival slip
POST /api/v1/quality-control/arrival-slips/{id}/inspection/    # Create/update inspection
GET  /api/v1/quality-control/inspections/{id}/                 # Get inspection by ID
GET  /api/v1/quality-control/inspections/{id}/parameters/      # Get parameter results
POST /api/v1/quality-control/inspections/{id}/parameters/      # Update parameter results
POST /api/v1/quality-control/inspections/{id}/submit/          # Submit for approval
```

### Approval APIs
```
POST /api/v1/quality-control/inspections/{id}/approve/chemist/ # QA Chemist approval
POST /api/v1/quality-control/inspections/{id}/approve/qam/     # QA Manager approval
POST /api/v1/quality-control/inspections/{id}/reject/          # Reject (back to Security Guard)
```

### Master Data APIs (Admin)
```
GET/POST /api/v1/quality-control/material-types/               # List/Create material types
GET/PUT/DELETE /api/v1/quality-control/material-types/{id}/    # Material type detail
GET/POST /api/v1/quality-control/material-types/{id}/parameters/ # QC parameters for material type
GET/PUT/DELETE /api/v1/quality-control/parameters/{id}/        # Parameter detail
```

---

## Rejection Workflow

When QA rejects an inspection:
```
QA Rejects Inspection
        ↓
Inspection status → REJECTED
Arrival Slip status → REJECTED
        ↓
Gate Entry status → ARRIVAL_SLIP_REJECTED
        ↓
Security Guard notified
        ↓
Security Guard updates Arrival Slip
        ↓
Resubmit to QA
        ↓
QA creates new inspection
```

---

## Permission-Based Access Control

Uses Django's built-in permission system. Assign permissions to users via Django Admin.

### Available Permissions

| Permission | Codename | Description |
|------------|----------|-------------|
| Can create arrival slip | `can_create_arrival_slip` | Create material arrival slips |
| Can edit arrival slip | `can_edit_arrival_slip` | Edit material arrival slips |
| Can submit arrival slip | `can_submit_arrival_slip` | Submit arrival slips to QA |
| Can view arrival slip | `can_view_arrival_slip` | View material arrival slips |
| Can create inspection | `can_create_inspection` | Create raw material inspections |
| Can edit inspection | `can_edit_inspection` | Edit raw material inspections |
| Can submit inspection | `can_submit_inspection` | Submit inspections for approval |
| Can view inspection | `can_view_inspection` | View raw material inspections |
| Can approve as chemist | `can_approve_as_chemist` | Approve as QA Chemist |
| Can approve as QAM | `can_approve_as_qam` | Approve as QA Manager |
| Can reject inspection | `can_reject_inspection` | Reject inspections |
| Can manage material types | `can_manage_material_types` | Manage material type master data |
| Can manage QC parameters | `can_manage_qc_parameters` | Manage QC parameter definitions |

### Typical Permission Groups
| User Type | Permissions |
|-----------|-------------|
| Security Guard | `can_create_arrival_slip`, `can_edit_arrival_slip`, `can_submit_arrival_slip`, `can_view_arrival_slip` |
| QA Technician | `can_create_inspection`, `can_edit_inspection`, `can_submit_inspection`, `can_view_inspection` |
| QA Chemist | All QA Technician + `can_approve_as_chemist`, `can_reject_inspection`, `can_manage_qc_parameters` |
| QA Manager | All QA Chemist + `can_approve_as_qam`, `can_manage_material_types` |

---

## Files Created/Modified

### New Files Created
| File | Purpose |
|------|---------|
| `quality_control/models/material_arrival_slip.py` | Arrival slip model |
| `quality_control/models/material_type.py` | Material type master |
| `quality_control/models/qc_parameter_master.py` | Parameter definitions |
| `quality_control/models/raw_material_inspection.py` | Inspection model |
| `quality_control/models/inspection_parameter_result.py` | Parameter results |
| `quality_control/permissions.py` | Permission-based access control |
| `quality_control/api_doc.md` | API documentation |

### Files Modified
| File | Changes |
|------|---------|
| `quality_control/enums.py` | Added new enums |
| `quality_control/serializers.py` | Added new serializers |
| `quality_control/views.py` | Added new API views |
| `quality_control/urls.py` | Added new endpoints |
| `quality_control/admin.py` | Added admin for new models |
| `quality_control/models/__init__.py` | Export new models |
| `gate_core/enums.py` | Added new status states |
| `gate_core/models/gate_entry.py` | Increased status max_length |

---

## Implementation Order

1. Create enums
2. Create MaterialType and QCParameterMaster models
3. Create MaterialArrivalSlip model and APIs
4. Create RawMaterialInspection and InspectionParameterResult models
5. Create inspection APIs
6. Create approval chain APIs
7. Update gate entry status flow
8. Add permissions
9. Write tests
