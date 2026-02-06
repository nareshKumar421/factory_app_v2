# Raw Material Gate-In Module

## Overview

The **Raw Material Gate-In Module** handles Purchase Order (PO) receipt processing for raw materials. It integrates with SAP to fetch PO data and validates received quantities against ordered quantities.

---

## Models

### POReceipt

| Field | Type | Description |
|-------|------|-------------|
| `vehicle_entry` | ForeignKey | Link to VehicleEntry (CASCADE) |
| `po_number` | CharField(30) | SAP Purchase Order number |
| `supplier_code` | CharField(30) | SAP Supplier code |
| `supplier_name` | CharField(150) | Supplier name |
| `invoice_no` | CharField(50) | Invoice number |
| `invoice_date` | DateField | Invoice date |
| `challan_no` | CharField(50) | Delivery challan number |
| `created_at` | DateTimeField | Auto-generated |
| `created_by` | ForeignKey | User who created |

**Constraints:** Unique together (vehicle_entry, po_number)

### POItemReceipt

| Field | Type | Description |
|-------|------|-------------|
| `po_receipt` | ForeignKey | Link to POReceipt (CASCADE) |
| `po_item_code` | CharField(50) | SAP PO item code |
| `item_name` | CharField(200) | Item description |
| `ordered_qty` | DecimalField | Quantity ordered |
| `received_qty` | DecimalField | Quantity received |
| `accepted_qty` | DecimalField | Quantity accepted (after QC) |
| `rejected_qty` | DecimalField | Quantity rejected (after QC) |
| `short_qty` | DecimalField | Auto-calculated (ordered - received) |
| `uom` | CharField(20) | Unit of measure |
| `created_at` | DateTimeField | Auto-generated |
| `created_by` | ForeignKey | User who created |

**Constraints:** Unique together (po_receipt, po_item_code)

---

## API Documentation

### Base URL
```
/api/v1/raw-material-gatein/
```

### Headers Required
```
Authorization: Bearer <access_token>
Company-Code: <company_code>
```

---

### 1. Receive PO Items

```
POST /api/v1/raw-material-gatein/gate-entries/{gate_entry_id}/po-receipts/
```

**Request Body:**
```json
{
    "po_number": "PO-2026-001",
    "supplier_code": "SUP001",
    "supplier_name": "ABC Suppliers Pvt Ltd",
    "items": [
        {
            "po_item_code": "ITEM001",
            "item_name": "Raw Material A",
            "ordered_qty": 1000.000,
            "received_qty": 950.000,
            "uom": "KG"
        },
        {
            "po_item_code": "ITEM002",
            "item_name": "Raw Material B",
            "ordered_qty": 500.000,
            "received_qty": 500.000,
            "uom": "LTR"
        }
    ]
}
```

**Response (201 Created):**
```json
{
    "message": "PO items received successfully"
}
```

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Invalid PO item {item_code}` |
| 400 | `Received quantity exceeds remaining quantity` |
| 502 | `Failed to retrieve PO data from SAP` |
| 503 | `SAP system is currently unavailable` |

**Note:** This endpoint:
1. Validates items against SAP remaining quantities
2. Creates POReceipt and POItemReceipt records
3. Changes gate entry status from `IN_PROGRESS` to `QC_PENDING`

---

### 2. List PO Receipts for Gate Entry

```
GET /api/v1/raw-material-gatein/gate-entries/{gate_entry_id}/po-receipts/view/
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "po_number": "PO-2026-001",
        "supplier_code": "SUP001",
        "supplier_name": "ABC Suppliers Pvt Ltd",
        "items": [
            {
                "id": 1,
                "po_item_code": "ITEM001",
                "item_name": "Raw Material A",
                "ordered_qty": "1000.000",
                "received_qty": "950.000",
                "short_qty": "50.000",
                "uom": "KG"
            },
            {
                "id": 2,
                "po_item_code": "ITEM002",
                "item_name": "Raw Material B",
                "ordered_qty": "500.000",
                "received_qty": "500.000",
                "short_qty": "0.000",
                "uom": "LTR"
            }
        ]
    }
]
```

---

### 3. Complete Gate Entry

```
POST /api/v1/raw-material-gatein/gate-entries/{gate_entry_id}/complete/
```

**Request Body:** None required

**Response (200 OK):**
```json
{
    "message": "Gate entry completed successfully"
}
```

**Validation Rules:**
- Entry type must be `RAW_MATERIAL`
- Security check must be completed and submitted
- PO receipts must exist
- All QC inspections must be completed (PASSED or FAILED)
- Weighment must be recorded

---

## Raw Material Gate-In Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    RAW MATERIAL GATE-IN FLOW                              │
└──────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │ Gate Entry   │
    │   Created    │ ──► entry_type = "RAW_MATERIAL"
    └──────┬───────┘     Status: DRAFT
           │
           ▼
    ┌──────────────┐
    │   Security   │
    │    Check     │ ──► Vehicle inspection, alcohol test
    └──────┬───────┘     Status: IN_PROGRESS
           │
           ▼
    ┌──────────────┐
    │  Weighment   │
    │   (Gross)    │ ──► First weighment - loaded vehicle
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  PO Receipt  │
    │   (SAP)      │ ──► POST /po-receipts/
    └──────┬───────┘     Status: QC_PENDING
           │
           ▼
    ┌──────────────┐
    │     QC       │
    │ Inspection   │ ──► Quality check for each item
    └──────┬───────┘     Status: QC_COMPLETED (when all done)
           │
           ▼
    ┌──────────────┐
    │  Weighment   │
    │   (Tare)     │ ──► Second weighment - empty vehicle
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Complete   │
    │     Entry    │ ──► POST /complete/
    └──────────────┘     Status: COMPLETED, is_locked = True
```

---

## Quantity Validation

The module validates that:
1. `received_qty <= remaining_qty` (from SAP)
2. `short_qty = ordered_qty - received_qty` (auto-calculated)

---

## Module Structure

```
raw_material_gatein/
├── __init__.py
├── apps.py
├── models/
│   ├── __init__.py
│   ├── po_receipt.py       # POReceipt model
│   └── po_item_receipt.py  # POItemReceipt model
├── serializers.py          # Request/Response serializers
├── views.py                # API views
├── urls.py                 # URL routing
├── services/
│   ├── __init__.py
│   ├── validation.py       # Quantity validation
│   └── completion.py       # Gate entry completion
├── admin.py                # Admin configuration
└── migrations/
```

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `sap_client` | Fetches open POs and validates quantities |
| `quality_control` | QC inspection for each PO item |
| `weighment` | Gross and tare weight measurement |
