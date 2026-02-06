# Raw Material Gate-In API Documentation

## Base URL
```
/api/v1/raw-material-gatein/
```

## Headers Required
```
Authorization: Bearer <access_token>
Company-Code: <company_code>
```

---

## Endpoints

### 1. Receive PO Items

Receive raw material PO items against a vehicle entry.

```
POST /api/v1/raw-material-gatein/gate-entries/{gate_entry_id}/po-receipts/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `raw_material_gatein.can_receive_po`

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
| 403 | `You do not have permission to perform this action.` |
| 502 | `Failed to retrieve PO data from SAP` |
| 503 | `SAP system is currently unavailable` |

**Notes:**
- Validates items against SAP remaining quantities
- Creates POReceipt and POItemReceipt records
- Changes gate entry status from `IN_PROGRESS` to `QC_PENDING`

---

### 2. List PO Receipts for Gate Entry

List all PO receipts for a specific gate entry.

```
GET /api/v1/raw-material-gatein/gate-entries/{gate_entry_id}/po-receipts/view/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `raw_material_gatein.can_view_po_receipt`

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

Complete and lock a gate entry.

```
POST /api/v1/raw-material-gatein/gate-entries/{gate_entry_id}/complete/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `raw_material_gatein.can_complete_raw_material_entry`

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

## Permission Summary

| Endpoint | Method | Permission Codename |
|----------|--------|---------------------|
| `/gate-entries/{id}/po-receipts/` | POST | `can_receive_po` |
| `/gate-entries/{id}/po-receipts/view/` | GET | `can_view_po_receipt` |
| `/gate-entries/{id}/complete/` | POST | `can_complete_raw_material_entry` |

## All Permissions

| Permission Codename | Description |
|---------------------|-------------|
| `raw_material_gatein.can_create_raw_material_entry` | Can create raw material gate entry |
| `raw_material_gatein.can_view_raw_material_entry` | Can view raw material gate entry |
| `raw_material_gatein.can_edit_raw_material_entry` | Can edit raw material gate entry |
| `raw_material_gatein.can_delete_raw_material_entry` | Can delete raw material gate entry |
| `raw_material_gatein.can_complete_raw_material_entry` | Can complete raw material gate entry |
| `raw_material_gatein.can_receive_po` | Can receive PO items |
| `raw_material_gatein.can_view_po_receipt` | Can view PO receipts |
| `raw_material_gatein.can_edit_po_receipt` | Can edit PO receipts |
| `raw_material_gatein.can_delete_po_receipt` | Can delete PO receipts |

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
