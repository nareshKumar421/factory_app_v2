# Quality Control - Complete Flow Documentation

## Overview

This document explains the complete flow of raw material gate entry from vehicle arrival to gate completion, including all the steps involved in quality control inspection.

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        RAW MATERIAL GATE ENTRY FLOW                              │
└─────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │  VEHICLE ARRIVES │
    │   at Factory     │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  GATE ENTRY      │ ──► Status: DRAFT
    │  Created         │     VehicleEntry record created
    │  (Security)      │     Driver & Vehicle registered
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  SECURITY CHECK  │ ──► Vehicle condition, tyres, fire extinguisher
    │  (Security Guard)│     Alcohol test for driver
    │                  │     Submit security check
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │   WEIGHMENT      │ ──► Gross weight recorded
    │  (Weighbridge)   │     Status: IN_PROGRESS
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │   PO RECEIPT     │ ──► GRPO API creates POReceipt
    │   (Store/ERP)    │     POItemReceipt for each line item
    │                  │     Status: QC_PENDING
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────────────────────────────────────────────────┐
    │                   FOR EACH PO ITEM                            │
    │  ┌──────────────────────────────────────────────────────────┐│
    │  │                                                          ││
    │  │  ┌──────────────────┐                                    ││
    │  │  │ ARRIVAL SLIP     │ ──► Security Guard fills:          ││
    │  │  │ (Security Guard) │     - Particulars, Party name      ││
    │  │  │                  │     - Transport details            ││
    │  │  │                  │     - Document references          ││
    │  │  │                  │     - Certificates info            ││
    │  │  │                  │     Submit to QA                   ││
    │  │  └────────┬─────────┘                                    ││
    │  │           │                                              ││
    │  │           ▼                                              ││
    │  │  ┌──────────────────┐                                    ││
    │  │  │ RAW MATERIAL     │ ──► QA Technician fills:           ││
    │  │  │ INSPECTION       │     - Material details             ││
    │  │  │ (QA Technician)  │     - Supplier/Manufacturer info   ││
    │  │  │                  │     - Batch/Lot numbers            ││
    │  │  │                  │     - Link Material Type           ││
    │  │  └────────┬─────────┘                                    ││
    │  │           │                                              ││
    │  │           ▼                                              ││
    │  │  ┌──────────────────┐                                    ││
    │  │  │ PARAMETER        │ ──► QA Technician records:         ││
    │  │  │ RESULTS          │     - Test results for each        ││
    │  │  │ (QA Technician)  │       QC parameter                 ││
    │  │  │                  │     - Numeric/Text values          ││
    │  │  │                  │     - Within spec check            ││
    │  │  └────────┬─────────┘                                    ││
    │  │           │                                              ││
    │  │           ▼                                              ││
    │  │  ┌──────────────────┐                                    ││
    │  │  │ SUBMIT FOR       │ ──► Workflow: SUBMITTED            ││
    │  │  │ APPROVAL         │                                    ││
    │  │  └────────┬─────────┘                                    ││
    │  │           │                                              ││
    │  │           ▼                                              ││
    │  │  ┌──────────────────┐                                    ││
    │  │  │ QA CHEMIST       │ ──► Review results                 ││
    │  │  │ APPROVAL         │     Approve/Reject                 ││
    │  │  │                  │     Workflow: QA_CHEMIST_APPROVED  ││
    │  │  └────────┬─────────┘                                    ││
    │  │           │                                              ││
    │  │           ▼                                              ││
    │  │  ┌──────────────────┐                                    ││
    │  │  │ QA MANAGER       │ ──► Final review                   ││
    │  │  │ APPROVAL         │     Set final_status:              ││
    │  │  │                  │     ACCEPTED / REJECTED / HOLD     ││
    │  │  │                  │     Workflow: QAM_APPROVED         ││
    │  │  └────────┬─────────┘                                    ││
    │  │           │                                              ││
    │  │           ▼                                              ││
    │  │  ┌──────────────────┐                                    ││
    │  │  │ INSPECTION       │ ──► final_status = ACCEPTED        ││
    │  │  │ COMPLETED        │     or REJECTED                    ││
    │  │  │                  │     Workflow: COMPLETED            ││
    │  │  └──────────────────┘                                    ││
    │  │                                                          ││
    │  └──────────────────────────────────────────────────────────┘│
    └──────────────────────────────────────────────────────────────┘
             │
             │ All PO items have inspection
             │ with ACCEPTED or REJECTED status
             ▼
    ┌──────────────────┐
    │   TARE WEIGHT    │ ──► Empty vehicle weighed
    │  (Weighbridge)   │     Net weight calculated
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  QC COMPLETED    │ ──► Status: QC_COMPLETED
    │                  │     All items inspected
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  GATE ENTRY      │ ──► Status: COMPLETED
    │  COMPLETED       │     Entry locked (is_locked=True)
    │                  │     Vehicle exits
    └──────────────────┘
```

---

## Data Model Relationships

```
VehicleEntry (Gate Entry)
    │
    ├── SecurityCheck (OneToOne)
    │
    ├── Weighment (OneToOne)
    │
    └── POReceipt (ForeignKey - Multiple)
            │
            └── POItemReceipt (ForeignKey - Multiple)
                    │
                    └── MaterialArrivalSlip (OneToOne)
                            │
                            └── RawMaterialInspection (OneToOne)
                                    │
                                    └── InspectionParameterResult (ForeignKey - Multiple)
```

---

## Step-by-Step Process

### Step 1: Vehicle Arrival & Gate Entry Creation

**Who:** Security Guard
**System:** Gate Entry Module

1. Vehicle arrives at factory gate
2. Security creates new gate entry (VehicleEntry)
3. Driver and vehicle details recorded
4. Entry status: `DRAFT`

**API:** `POST /api/v1/gate-entry/`

---

### Step 2: Security Check

**Who:** Security Guard
**System:** Security Checks Module

1. Check vehicle condition (body, tyres)
2. Verify fire extinguisher availability
3. Conduct alcohol test for driver
4. Submit security check

**API:** `POST /api/v1/security-check/{gate_entry_id}/`

---

### Step 3: Weighment (Gross Weight)

**Who:** Weighbridge Operator
**System:** Weighment Module

1. Vehicle enters weighbridge
2. Record gross weight
3. Entry status changes to: `IN_PROGRESS`

**API:** `POST /api/v1/weighment/{gate_entry_id}/`

---

### Step 4: PO Receipt (GRPO)

**Who:** Store/ERP System
**System:** Raw Material Gate-In Module

1. GRPO data received from SAP/ERP
2. Create POReceipt with PO details
3. Create POItemReceipt for each line item
4. Entry status changes to: `QC_PENDING`

**API:** `POST /api/v1/grpo/`

---

### Step 5: Material Arrival Slip (For Each PO Item)

**Who:** Security Guard
**System:** Quality Control Module

1. Security Guard creates arrival slip for each PO item
2. Fill arrival details:
   - Particulars of material
   - Party name and billing details
   - Transport details (truck number)
   - Document references (invoice, e-way bill, bilty)
   - Certificate information (COA, COQ)
3. Submit arrival slip to QA

**API:** `POST /api/v1/quality-control/po-items/{po_item_id}/arrival-slip/`

**Arrival Slip Status Flow:**
```
DRAFT → SUBMITTED → (QA can reject → REJECTED)
```

---

### Step 6: Raw Material Inspection (For Each Arrival Slip)

**Who:** QA Technician
**System:** Quality Control Module

1. QA Technician creates inspection for arrival slip
2. Fill inspection details:
   - Description of material
   - SAP code
   - Material type (links to QC parameters)
   - Supplier and manufacturer info
   - Batch/Lot numbers
   - Vehicle number
3. Auto-generated: Report No, Internal Lot No

**API:** `POST /api/v1/quality-control/arrival-slips/{slip_id}/inspection/`

**Inspection Workflow Status:**
```
DRAFT → SUBMITTED → QA_CHEMIST_APPROVED → QAM_APPROVED → COMPLETED
```

---

### Step 7: Parameter Test Results

**Who:** QA Technician / Lab
**System:** Quality Control Module

1. Based on material type, QC parameters are loaded
2. QA Technician records test results:
   - Numeric values (weight, pH, etc.)
   - Text values (colour, appearance)
   - Boolean values (pass/fail)
3. System checks if values are within specification

**API:** `POST /api/v1/quality-control/inspections/{inspection_id}/parameters/`

**Example Parameters:**
| Parameter | Standard | Result | Within Spec |
|-----------|----------|--------|-------------|
| Weight    | 50 KG    | 49.5   | Yes         |
| pH        | 6.5-7.5  | 7.0    | Yes         |
| Colour    | White    | White  | Yes         |
| Moisture  | <5%      | 4.2%   | Yes         |

---

### Step 8: Submit for Approval

**Who:** QA Technician
**System:** Quality Control Module

1. QA Technician submits inspection for approval
2. Workflow status: `SUBMITTED`

**API:** `POST /api/v1/quality-control/inspections/{inspection_id}/submit/`

---

### Step 9: QA Chemist Approval

**Who:** QA Chemist
**System:** Quality Control Module

**Permission Required:** `quality_control.can_approve_as_chemist`

1. QA Chemist reviews inspection results
2. Add remarks if needed
3. Approve inspection
4. Workflow status: `QA_CHEMIST_APPROVED`

**API:** `POST /api/v1/quality-control/inspections/{inspection_id}/approve/chemist/`

---

### Step 10: QA Manager (QAM) Approval

**Who:** QA Manager
**System:** Quality Control Module

**Permission Required:** `quality_control.can_approve_as_qam`

1. QA Manager does final review
2. Set final status:
   - `ACCEPTED` - Material approved for use
   - `REJECTED` - Material rejected
   - `HOLD` - Material on hold for further review
3. Workflow status: `QAM_APPROVED` then `COMPLETED`

**API:** `POST /api/v1/quality-control/inspections/{inspection_id}/approve/qam/`

---

### Step 11: Tare Weight

**Who:** Weighbridge Operator
**System:** Weighment Module

1. After unloading, empty vehicle weighed
2. Record tare weight
3. System calculates net weight

**API:** `PUT /api/v1/weighment/{gate_entry_id}/`

---

### Step 12: Gate Completion

**Who:** System / Operator
**System:** Gate Core Module

**Completion Rules:**
1. Security check must be submitted
2. Weighment must be completed
3. At least one PO item must exist
4. **All PO items must have inspection with final_status = ACCEPTED or REJECTED**

When all conditions are met:
1. Status changes to: `QC_COMPLETED`
2. Then status changes to: `COMPLETED`
3. Entry is locked (`is_locked = True`)
4. Vehicle can exit

**API:** `POST /api/v1/gate-entry/{gate_entry_id}/complete/`

---

## Status Flow Summary

### Gate Entry Status
```
DRAFT → IN_PROGRESS → QC_PENDING → QC_COMPLETED → COMPLETED
```

### Arrival Slip Status
```
DRAFT → SUBMITTED (→ REJECTED if QA rejects)
```

### Inspection Workflow Status
```
DRAFT → SUBMITTED → QA_CHEMIST_APPROVED → QAM_APPROVED → COMPLETED
```

### Inspection Final Status
```
PENDING → ACCEPTED / REJECTED / HOLD
```

---

## User Roles & Permissions

| Role | Actions |
|------|---------|
| **Security Guard** | Create gate entry, security check, arrival slips |
| **Weighbridge Operator** | Record gross/tare weights |
| **Store Operator** | Process GRPO data |
| **QA Technician** | Create inspection, record test results, submit |
| **QA Chemist** | Review and approve inspection (chemist level) |
| **QA Manager** | Final approval, set ACCEPTED/REJECTED/HOLD |

---

## API Endpoints Summary

| Step | Endpoint | Method |
|------|----------|--------|
| Gate Entry | `/api/v1/gate-entry/` | POST |
| Security Check | `/api/v1/security-check/{id}/` | POST |
| Weighment | `/api/v1/weighment/{id}/` | POST/PUT |
| GRPO | `/api/v1/grpo/` | POST |
| Arrival Slip | `/api/v1/quality-control/po-items/{id}/arrival-slip/` | POST |
| Arrival Slip Submit | `/api/v1/quality-control/arrival-slips/{id}/submit/` | POST |
| Inspection | `/api/v1/quality-control/arrival-slips/{id}/inspection/` | POST |
| Parameters | `/api/v1/quality-control/inspections/{id}/parameters/` | POST |
| Submit Inspection | `/api/v1/quality-control/inspections/{id}/submit/` | POST |
| Chemist Approve | `/api/v1/quality-control/inspections/{id}/approve/chemist/` | POST |
| QAM Approve | `/api/v1/quality-control/inspections/{id}/approve/qam/` | POST |
| Complete Gate | `/api/v1/gate-entry/{id}/complete/` | POST |

---

## Key Business Rules

1. **One Arrival Slip per PO Item** - Each PO item gets exactly one arrival slip
2. **One Inspection per Arrival Slip** - Each arrival slip gets exactly one inspection
3. **Dynamic QC Parameters** - Parameters are based on material type
4. **Sequential Approval** - Must follow: Technician → Chemist → Manager
5. **Gate Completion** - All items must have ACCEPTED or REJECTED status
6. **Locking** - Completed entries cannot be modified

---

## Error Scenarios

| Scenario | Resolution |
|----------|------------|
| QA rejects arrival slip | Security Guard corrects and resubmits |
| QA Chemist rejects | Technician reviews and resubmits |
| Material on HOLD | QA Manager reviews later, changes to ACCEPTED/REJECTED |
| Missing inspection | Gate cannot complete until all items have inspection |
| Incomplete parameters | Inspection cannot be submitted |
