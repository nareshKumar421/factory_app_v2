# Quality Control - Status Flow Documentation

## 1. Gate Entry Status Flow (VehicleEntry.status)

The `GateEntryStatus` enum tracks the overall progress of a vehicle entry through the gate process.

### Status Definitions

| Status                   | Display                  | Description                                      |
|--------------------------|--------------------------|--------------------------------------------------|
| `DRAFT`                  | Draft                    | Entry created, no action taken yet               |
| `IN_PROGRESS`            | In Progress              | Security check started                           |
| `ARRIVAL_SLIP_SUBMITTED` | Arrival Slip Submitted   | Security guard submitted arrival slip to QA      |
| `ARRIVAL_SLIP_REJECTED`  | Arrival Slip Rejected    | Arrival slip rejected by QA                      |
| `QC_PENDING`             | QC Pending               | Inspection created, awaiting lab results         |
| `QC_IN_REVIEW`           | QC In Review             | Inspection submitted for QA Chemist review       |
| `QC_AWAITING_QAM`        | Awaiting QAM Approval    | QA Chemist approved, awaiting QA Manager         |
| `QC_REJECTED`            | QC Rejected              | One or more items rejected during QC             |
| `QC_COMPLETED`           | QC Completed             | All items have final QC decision (accepted/rejected) |
| `COMPLETED`              | Completed                | Gate entry fully completed and locked            |
| `CANCELLED`              | Cancelled                | Entry cancelled                                  |

### Transition Diagram

```
DRAFT
  |
  v
IN_PROGRESS  (security check created)
  |
  v
ARRIVAL_SLIP_SUBMITTED  (arrival slip submitted to QA)
  |          |
  |          v
  |   ARRIVAL_SLIP_REJECTED  (QA rejects arrival slip)
  |          |
  |          +---> ARRIVAL_SLIP_SUBMITTED  (resubmit)
  |
  v
QC_PENDING  (inspection created)
  |
  v
QC_IN_REVIEW  (inspection submitted for chemist review)
  |          |
  |          +---> QC_REJECTED  (inspection rejected)
  v                    |
QC_AWAITING_QAM        |
  |          |         |
  |          +---> QC_REJECTED
  v                    |
QC_COMPLETED  <--------+  (all items have final decision)
  |
  v
COMPLETED  (gate entry locked)
```

### Allowed Transitions (status_guard.py)

| From                     | Allowed To                                              |
|--------------------------|---------------------------------------------------------|
| `DRAFT`                  | `IN_PROGRESS`                                           |
| `IN_PROGRESS`            | `QC_PENDING`, `ARRIVAL_SLIP_SUBMITTED`                  |
| `ARRIVAL_SLIP_SUBMITTED` | `QC_PENDING`, `ARRIVAL_SLIP_REJECTED`                   |
| `ARRIVAL_SLIP_REJECTED`  | `ARRIVAL_SLIP_SUBMITTED`                                |
| `QC_PENDING`             | `QC_IN_REVIEW`, `QC_COMPLETED`                          |
| `QC_IN_REVIEW`           | `QC_AWAITING_QAM`, `QC_REJECTED`, `QC_COMPLETED`       |
| `QC_AWAITING_QAM`        | `QC_COMPLETED`, `QC_REJECTED`                           |
| `QC_REJECTED`            | `QC_COMPLETED`, `COMPLETED`                             |
| `QC_COMPLETED`           | `COMPLETED`                                             |

---

## 2. Inspection Workflow Status (RawMaterialInspection.workflow_status)

Tracks the approval chain progress of an individual QC inspection.

### Status Definitions

| Status                 | Display              | Description                            |
|------------------------|----------------------|----------------------------------------|
| `DRAFT`                | Draft                | Inspection created, results being entered |
| `SUBMITTED`            | Submitted            | Submitted for QA Chemist review        |
| `QA_CHEMIST_APPROVED`  | QA Chemist Approved  | QA Chemist approved the results        |
| `QAM_APPROVED`         | QAM Approved         | QA Manager gave final approval         |
| `REJECTED`             | Rejected             | Inspection rejected by QA              |
| `COMPLETED`            | Completed            | Legacy terminal state                  |

### Transition Diagram

```
DRAFT
  |
  v
SUBMITTED  (submit for chemist review)
  |          |
  |          +---> REJECTED  (rejected at chemist stage)
  v
QA_CHEMIST_APPROVED
  |          |
  |          +---> REJECTED  (rejected at QAM stage)
  v
QAM_APPROVED  (final - locked)
```

### Key Rules

- Rejection can happen at `SUBMITTED` or `QA_CHEMIST_APPROVED` stage
- Once rejected: `is_locked = True`, `final_status = REJECTED`
- Once QAM approved: `is_locked = True`, `final_status = ACCEPTED/REJECTED/HOLD`
- Locked inspections cannot be modified or rejected again

---

## 3. Inspection Final Status (RawMaterialInspection.final_status)

The QA Manager's final decision on the material quality.

| Status     | Description                                  |
|------------|----------------------------------------------|
| `PENDING`  | No decision yet (default)                    |
| `ACCEPTED` | Material accepted, proceed to GRPO           |
| `REJECTED` | Material rejected, send back                 |
| `HOLD`     | Material on hold for further review          |

---

## 4. Arrival Slip Status (MaterialArrivalSlip.status)

| Status      | Description                              |
|-------------|------------------------------------------|
| `DRAFT`     | Created by security guard, not submitted |
| `SUBMITTED` | Submitted to QA for inspection           |
| `REJECTED`  | Rejected by QA, sent back to security    |

---

## 5. Smart Entry Status Calculation (compute_entry_status)

For multi-item entries (multiple PO items), the gate entry status reflects the
**overall QC progress** across all items. The `update_entry_status()` function
in `quality_control/services/rules.py` is the single source of truth.

### Logic

1. If **all items** are terminal (`QAM_APPROVED` or `REJECTED`) -> `QC_COMPLETED`
2. If **any item** is `REJECTED` but others aren't done -> `QC_REJECTED`
3. If the **furthest item** reached `QA_CHEMIST_APPROVED` -> `QC_AWAITING_QAM`
4. If the **furthest item** reached `SUBMITTED` -> `QC_IN_REVIEW`
5. Otherwise -> `QC_PENDING`

### Where It's Called

Every QC action calls `update_entry_status(entry)` after modifying the inspection:

| API                          | Action                     | File                        |
|------------------------------|----------------------------|-----------------------------|
| `InspectionCreateUpdateAPI`  | Inspection created/updated | `quality_control/views.py`  |
| `InspectionSubmitAPI`        | Submitted for chemist      | `quality_control/views.py`  |
| `InspectionApproveChemistAPI`| Chemist approved           | `quality_control/views.py`  |
| `InspectionApproveQAMAPI`    | QAM approved               | `quality_control/views.py`  |
| `InspectionRejectAPI`        | Rejected                   | `quality_control/views.py`  |

### Exception: ArrivalSlipSubmitAPI

The arrival slip submission still uses direct status assignment (not `update_entry_status`)
because it operates before the QC inspection flow begins:

- `IN_PROGRESS` -> `ARRIVAL_SLIP_SUBMITTED`
- `ARRIVAL_SLIP_REJECTED` -> `ARRIVAL_SLIP_SUBMITTED` (resubmission)

---

## 6. Gate Completion (gate_completion.py)

The `complete_gate_entry()` service in `raw_material_gatein/services/gate_completion.py`
handles final gate completion.

### Prerequisites

1. Security check exists and is submitted
2. Weighment exists
3. At least one PO item received
4. All PO items have completed QC (`final_status` is `ACCEPTED` or `REJECTED`)

### Status Handling

Regardless of current status, the service transitions through:

1. Any intermediate QC status (`QC_PENDING`, `QC_IN_REVIEW`, `QC_AWAITING_QAM`, `QC_REJECTED`) -> `QC_COMPLETED`
2. `QC_COMPLETED` -> `COMPLETED` (entry locked)

---

## 7. Rejection Flow (End-to-End)

When QC inspection is rejected:

### Step 1: API Call
`POST /api/v1/quality-control/inspections/{id}/reject/`

### Step 2: Validation
- Inspection must not be locked
- Workflow status must be `SUBMITTED` or `QA_CHEMIST_APPROVED`

### Step 3: Inspection Update (reject method)
- `final_status` = `REJECTED`
- `workflow_status` = `REJECTED`
- `is_locked` = `True`
- `rejected_by` = requesting user
- `rejected_at` = current timestamp
- `remarks` = rejection remarks

### Step 4: Arrival Slip Update (reject_by_qa)
- `status` = `REJECTED`
- `is_submitted` = `False`
- `remarks` = rejection remarks

### Step 5: Gate Entry Status Update (update_entry_status)
- If all items are terminal -> `QC_COMPLETED`
- If some items still in progress -> `QC_REJECTED`

### Step 6: Visibility
- Rejected items appear in `inspections/pending/` API with `inspection_status: "REJECTED"`
- Full view API shows `rejected_by` and `rejected_at` in inspection data
- QC summary in full view shows the item as `"REJECTED", "QC Rejected"`

---

## 8. API Endpoints

| Endpoint                                          | Method | Description                     |
|---------------------------------------------------|--------|---------------------------------|
| `inspections/pending/`                            | GET    | List pending + rejected items   |
| `arrival-slips/{id}/inspection/`                  | POST   | Create/update inspection        |
| `inspections/{id}/submit/`                        | POST   | Submit for chemist review       |
| `inspections/{id}/approve/chemist/`               | POST   | QA Chemist approval             |
| `inspections/{id}/approve/qam/`                   | POST   | QA Manager final approval       |
| `inspections/{id}/reject/`                        | POST   | Reject inspection               |

All endpoints require: `IsAuthenticated`, `HasCompanyContext`, and the relevant permission.

---

## 9. Permissions

| Permission                  | Who               | Action                         |
|-----------------------------|-------------------|--------------------------------|
| `can_submit_inspection`     | QA Lab Technician | Submit inspection for review   |
| `can_approve_as_chemist`    | QA Chemist        | Approve/review inspection      |
| `can_approve_as_qam`        | QA Manager        | Final approval with decision   |
| `can_reject_inspection`     | QA Chemist / QAM  | Reject inspection              |
