# SAP Client Module

## Overview

The **SAP Client Module** provides integration with SAP Business One for fetching Purchase Order (PO) data. It connects to SAP HANA database to retrieve open POs and their items for raw material gate-in processing.

---

## Configuration

SAP connection settings in `settings.py`:

```python
# SAP HANA Connection
HANA_HOST = "103.89.45.192"
HANA_PORT = 30015
HANA_USER = "DSR"
HANA_PASSWORD = "****"

# Service Layer
SL_URL = "https://103.89.45.192:50000"
SL_USER = "B1i"
SL_PASSWORD = "****"

# Company Database Mapping
COMPANY_DB = {
    "JIVO_OIL": "TEST_OIL_15122025",
    "JIVO_MART": "TEST_MART_15122025",
}
```

---

## Data Transfer Objects

### PO (Purchase Order)

| Field | Type | Description |
|-------|------|-------------|
| `po_number` | str | Purchase Order number |
| `supplier_code` | str | Supplier/Vendor code |
| `supplier_name` | str | Supplier name |
| `items` | List[POItem] | List of PO line items |

### POItem

| Field | Type | Description |
|-------|------|-------------|
| `po_item_code` | str | Line item code |
| `item_name` | str | Item description |
| `ordered_qty` | Decimal | Ordered quantity |
| `remaining_qty` | Decimal | Remaining quantity to receive |
| `uom` | str | Unit of measure |

---

## API Documentation

### Base URL
```
/api/v1/po/
```

### Headers Required
```
Authorization: Bearer <access_token>
Company-Code: <company_code>
```

---

### 1. List Open POs for Supplier

```
GET /api/v1/po/open-pos/?supplier_code=SUP001
```

**Query Parameters:**
- `supplier_code` (required): SAP supplier/vendor code

**Response (200 OK):**
```json
[
    {
        "po_number": "PO-2026-001",
        "supplier_code": "SUP001",
        "supplier_name": "ABC Suppliers Pvt Ltd",
        "items": [
            {
                "po_item_code": "ITEM001",
                "item_name": "Raw Material A",
                "ordered_qty": "1000.000",
                "remaining_qty": "500.000",
                "uom": "KG"
            },
            {
                "po_item_code": "ITEM002",
                "item_name": "Raw Material B",
                "ordered_qty": "500.000",
                "remaining_qty": "500.000",
                "uom": "LTR"
            }
        ]
    },
    {
        "po_number": "PO-2026-002",
        "supplier_code": "SUP001",
        "supplier_name": "ABC Suppliers Pvt Ltd",
        "items": [
            {
                "po_item_code": "ITEM003",
                "item_name": "Raw Material C",
                "ordered_qty": "200.000",
                "remaining_qty": "200.000",
                "uom": "PCS"
            }
        ]
    }
]
```

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `supplier_code is required` |
| 502 | `Failed to retrieve PO data from SAP` |
| 503 | `SAP system is currently unavailable` |

---

### 2. Get PO Items

```
GET /api/v1/po/open-pos/{po_number}/items/
```

**Response (200 OK):**
```json
{
    "po_number": "PO-2026-001",
    "supplier_code": "SUP001",
    "supplier_name": "ABC Suppliers Pvt Ltd",
    "items": [
        {
            "po_item_code": "ITEM001",
            "item_name": "Raw Material A",
            "ordered_qty": "1000.000",
            "remaining_qty": "500.000",
            "uom": "KG"
        },
        {
            "po_item_code": "ITEM002",
            "item_name": "Raw Material B",
            "ordered_qty": "500.000",
            "remaining_qty": "500.000",
            "uom": "LTR"
        }
    ]
}
```

**Error Response (404):**
```json
{
    "detail": "PO not found"
}
```

---

## SAP Integration Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                       SAP INTEGRATION FLOW                                │
└──────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   Frontend   │
    │   Request    │ ──► GET /open-pos/?supplier_code=SUP001
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  SAP Client  │
    │   Module     │ ──► Validates Company-Code header
    └──────┬───────┘     Maps to SAP database
           │
           ▼
    ┌──────────────┐
    │  SAP HANA    │
    │   Database   │ ──► Executes query for open POs
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Response   │
    │   Mapping    │ ──► Converts to PO/POItem DTOs
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   JSON       │
    │   Response   │ ──► Returns serialized PO data
    └──────────────┘
```

---

## Exception Handling

### SAPConnectionError
Raised when unable to connect to SAP HANA database.
- Returns HTTP 503 (Service Unavailable)

### SAPDataError
Raised when unable to parse or retrieve data from SAP.
- Returns HTTP 502 (Bad Gateway)

---

## Module Structure

```
sap_client/
├── __init__.py
├── apps.py
├── client.py               # SAPClient class
├── dto.py                  # PO, POItem data classes
├── exceptions.py           # SAPConnectionError, SAPDataError
├── serializers.py          # POSerializer, POItemSerializer
├── views.py                # API views
├── urls.py                 # URL routing
└── migrations/
```

---

## Usage in Other Modules

The `SAPClient` is used internally by `raw_material_gatein` module:

```python
from sap_client.client import SAPClient
from sap_client.exceptions import SAPConnectionError, SAPDataError

try:
    client = SAPClient(company_code="JIVO_OIL")
    po_list = client.get_open_pos(supplier_code="SUP001")
except SAPConnectionError:
    # Handle connection failure
except SAPDataError:
    # Handle data retrieval failure
```
