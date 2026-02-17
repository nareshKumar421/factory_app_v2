# QC Inspection API Documentation

## Design Decision

All list endpoints query from `MaterialArrivalSlip` (not `RawMaterialInspection`). Django's ORM creates a LEFT JOIN to the optional `inspection` automatically via `MaterialArrivalSlip.objects.filter(inspection__workflow_status=...)`. This ensures items without inspections are never lost.

```
MaterialArrivalSlip (always exists)
    └── .inspection (may or may not exist — LEFT JOIN)
```

## Base URL

```
/api/v1/quality-control/
```

All endpoints require:
- `Authorization: Bearer <token>`
- `Company-Code: <code>` header

---

## List Endpoints (Lightweight Serializer)

These endpoints return `InspectionListItemSerializer` — a lightweight response queried from `MaterialArrivalSlip`.

### Response Shape

```json
{
  "arrival_slip_id": 1,
  "inspection_id": 5,
  "entry_no": "GE-20260217-0001",
  "report_no": "RPT-20260217-0001",
  "item_name": "Steel Rod",
  "party_name": "ABC Suppliers",
  "billing_qty": "100.000",
  "billing_uom": "KG",
  "workflow_status": "NOT_STARTED",
  "final_status": null,
  "created_at": "2026-02-17T10:00:00Z",
  "submitted_at": "2026-02-17T10:30:00Z"
}
```

**`workflow_status` values:** `NOT_STARTED` (no inspection yet), `DRAFT`, `SUBMITTED`, `QA_CHEMIST_APPROVED`, `QAM_APPROVED`, `REJECTED`

**`final_status` values:** `null`, `PENDING`, `ACCEPTED`, `REJECTED`, `HOLD`

> `NOT_STARTED` is a computed serializer value (not a database state). It means no `RawMaterialInspection` record exists for this arrival slip.

### Common Query Parameters

| Param | Type | Description |
|-------|------|-------------|
| `from_date` | `YYYY-MM-DD` | Filter by `submitted_at >= date` |
| `to_date` | `YYYY-MM-DD` | Filter by `submitted_at <= date` |

---

### GET `/inspections/` — All Tab

Returns all submitted/rejected arrival slips regardless of inspection status.

**Permission:** `CanViewInspection`

---

### GET `/inspections/pending/` — Pending Tab

Returns arrival slips with **no inspection** created yet.

**Permission:** `CanViewInspection`

---

### GET `/inspections/draft/` — Draft Tab

Returns arrival slips where the inspection exists but is still in `DRAFT` status.

**Permission:** `CanViewInspection`

---

### GET `/inspections/actionable/` — Actionable Tab

Returns items that need action. Includes:
- No inspection (`NOT_STARTED`)
- `DRAFT` inspections
- `SUBMITTED` inspections (awaiting chemist)
- `QA_CHEMIST_APPROVED` inspections (awaiting QAM)

**Permission:** `CanViewInspection`

---

### GET `/inspections/completed/` — Approved Tab

Returns items where inspection has `workflow_status = QAM_APPROVED`.

| Param | Type | Description |
|-------|------|-------------|
| `final_status` | `string` | Optional. Filter by `ACCEPTED`, `REJECTED`, or `HOLD` |

**Permission:** `CanViewInspection`

**Usage examples:**
- Approved tab: `?final_status=ACCEPTED`
- On Hold items: `?final_status=HOLD`
- All completed: no param

---

### GET `/inspections/rejected/` — Rejected Tab

Returns items where `final_status = REJECTED`. Catches both rejection paths:
1. Rejected during review (`workflow_status=REJECTED`, `final_status=REJECTED`)
2. Rejected by QAM via approval (`workflow_status=QAM_APPROVED`, `final_status=REJECTED`)

**Permission:** `CanViewInspection`

---

### GET `/inspections/counts/` — Dashboard Counts

Returns counts for all statuses in a single DB query.

**Permission:** `CanViewInspection`

**Response:**

```json
{
  "not_started": 5,
  "draft": 3,
  "awaiting_chemist": 2,
  "awaiting_qam": 1,
  "completed": 10,
  "rejected": 2,
  "hold": 1,
  "actionable": 11
}
```

`actionable = not_started + draft + awaiting_chemist + awaiting_qam`

Supports `from_date` / `to_date` query params.

---

## Approval Queue Endpoints (Full Serializer)

These endpoints return `RawMaterialInspectionSerializer` — a full response with nested parameter results. Used by the approval queue pages.

### GET `/inspections/awaiting-chemist/`

Returns inspections with `workflow_status = SUBMITTED`.

**Permission:** `CanApproveAsChemist`

---

### GET `/inspections/awaiting-qam/`

Returns inspections with `workflow_status = QA_CHEMIST_APPROVED`.

**Permission:** `CanApproveAsQAM`

---

## Arrival Slip Endpoints

### GET `/arrival-slips/`

List all arrival slips for the company. Optional `?status=DRAFT|SUBMITTED|REJECTED` filter.

**Permission:** `CanViewArrivalSlip`

### GET `/arrival-slips/<slip_id>/`

Get arrival slip by ID.

**Permission:** `CanViewArrivalSlip`

### POST `/po-items/<po_item_id>/arrival-slip/`

Create or update arrival slip for a PO item. Uses `get_or_create` — creates on first call, updates on subsequent calls.

**Permission:** `CanManageArrivalSlip`

**Body:**

```json
{
  "particulars": "Steel rods, 10mm",
  "arrival_datetime": "2026-02-17T10:00:00Z",
  "weighing_required": false,
  "party_name": "ABC Suppliers",
  "billing_qty": "100.000",
  "billing_uom": "KG",
  "truck_no_as_per_bill": "MH-12-AB-1234",
  "commercial_invoice_no": "INV-001",
  "eway_bill_no": "EWB-001",
  "bilty_no": "BLT-001",
  "has_certificate_of_analysis": true,
  "has_certificate_of_quantity": false,
  "remarks": ""
}
```

### POST `/arrival-slips/<slip_id>/submit/`

Submit arrival slip to QA. Changes status from `DRAFT` to `SUBMITTED`.

**Permission:** `CanSubmitArrivalSlip`

---

## Inspection CRUD Endpoints

### GET `/arrival-slips/<slip_id>/inspection/`

Get inspection for an arrival slip.

**Permission:** `CanManageInspection`

### POST `/arrival-slips/<slip_id>/inspection/`

Create or update inspection for an arrival slip. Auto-generates `report_no` and `internal_lot_no`. If `material_type_id` is provided, auto-creates parameter result rows.

**Permission:** `CanManageInspection`

**Body:**

```json
{
  "inspection_date": "2026-02-17",
  "description_of_material": "Steel Rod 10mm",
  "sap_code": "SAP-001",
  "supplier_name": "ABC Suppliers",
  "manufacturer_name": "XYZ Manufacturing",
  "supplier_batch_lot_no": "BATCH-001",
  "unit_packing": "Bundle",
  "purchase_order_no": "PO-001",
  "invoice_bill_no": "INV-001",
  "vehicle_no": "MH-12-AB-1234",
  "material_type_id": 1,
  "remarks": ""
}
```

### GET `/inspections/<inspection_id>/`

Get full inspection detail by ID.

**Permission:** `CanViewInspection`

---

## Parameter Results

### GET `/inspections/<inspection_id>/parameters/`

List all parameter results for an inspection.

**Permission:** `CanManageInspection`

### POST `/inspections/<inspection_id>/parameters/`

Bulk update parameter results.

**Permission:** `CanManageInspection`

**Body:**

```json
{
  "results": [
    {
      "parameter_master_id": 1,
      "result_value": "7.2",
      "result_numeric": 7.2,
      "is_within_spec": true,
      "remarks": ""
    }
  ]
}
```

---

## Workflow Actions

### POST `/inspections/<inspection_id>/submit/`

Submit inspection for QA Chemist approval. Validates all mandatory parameters have results.

**Permission:** `CanSubmitInspection`

### POST `/inspections/<inspection_id>/approve/chemist/`

QA Chemist approves inspection. Moves workflow to `QA_CHEMIST_APPROVED`.

**Permission:** `CanApproveAsChemist`

**Body:**

```json
{
  "remarks": "Parameters within spec"
}
```

### POST `/inspections/<inspection_id>/approve/qam/`

QA Manager final approval. Sets `final_status` and moves workflow to `QAM_APPROVED`.

**Permission:** `CanApproveAsQAM`

**Body:**

```json
{
  "remarks": "Approved for use",
  "final_status": "ACCEPTED"
}
```

`final_status` options: `ACCEPTED`, `REJECTED`, `HOLD`

### POST `/inspections/<inspection_id>/reject/`

Reject inspection. Locks the inspection and marks the arrival slip as `REJECTED`.

**Permission:** `CanRejectInspection`

**Body:**

```json
{
  "remarks": "Parameters out of spec"
}
```

---

## Material Type & QC Parameter Master

### GET/POST `/material-types/`

List or create material types.

**Permission:** `CanManageMaterialTypes`

### GET/PUT/DELETE `/material-types/<id>/`

Get, update, or soft-delete a material type.

**Permission:** `CanManageMaterialTypes`

### GET/POST `/material-types/<id>/parameters/`

List or create QC parameters for a material type.

**Permission:** `CanManageQCParameters`

### GET/PUT/DELETE `/parameters/<id>/`

Get, update, or soft-delete a QC parameter.

**Permission:** `CanManageQCParameters`

---

## Workflow Status Flow

```
Arrival Slip:  DRAFT → SUBMITTED → (REJECTED → DRAFT → SUBMITTED → ...)

Inspection:    DRAFT → SUBMITTED → QA_CHEMIST_APPROVED → QAM_APPROVED
                          ↓                    ↓
                       REJECTED             REJECTED

Final Status (set by QAM): ACCEPTED | REJECTED | HOLD
```
