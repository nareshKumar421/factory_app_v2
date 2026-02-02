# GRPO API Documentation

## Overview

The GRPO (Goods Receipt PO) API allows creating Purchase Delivery Notes in SAP Business One via the Service Layer.

## Endpoint

```
POST /api/v1/po/grpo/
```

## Authentication

Requires JWT authentication and company context.

**Headers:**
| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes | `Bearer <access_token>` |
| `Company-Code` | Yes | Company code (e.g., `JIVO_OIL`, `JIVO_MART`) |
| `Content-Type` | Yes | `application/json` |

## Request Body

### Basic Example

```json
{
    "CardCode": "c001",
    "DocumentLines": [
        {
            "ItemCode": "c001",
            "Quantity": "100",
            "TaxCode": "T1",
            "UnitPrice": "50"
        }
    ]
}
```

### Full Example (with optional fields)

```json
{
    "CardCode": "VENDA000466",
    "BPL_IDAssignedToInvoice": 2,
    "DocDate": "2026-02-02",
    "DocDueDate": "2026-02-10",
    "Comments": "Received goods as per PO",
    "DocumentLines": [
        {
            "ItemCode": "PM0000073",
            "Quantity": "100",
            "TaxCode": "T1",
            "UnitPrice": "50.00",
            "WarehouseCode": "WH01"
        },
        {
            "ItemCode": "PM0000453",
            "Quantity": "50",
            "TaxCode": "T1",
            "UnitPrice": "75.00",
            "WarehouseCode": "WH01"
        }
    ]
}
```

### PO-Based GRPO (Copy from Purchase Order)

```json
{
    "CardCode": "V001",
    "DocumentLines": [
        {
            "ItemCode": "ITEM001",
            "Quantity": "100",
            "BaseEntry": 123,
            "BaseLine": 0,
            "BaseType": 22
        }
    ]
}
```

## Request Fields

### Document Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `CardCode` | string | Yes | Supplier/Vendor code |
| `BPL_IDAssignedToInvoice` | integer | No* | Branch/Business Place ID (*Required if multi-branch enabled) |
| `DocDate` | date | No | Document date (YYYY-MM-DD) |
| `DocDueDate` | date | No | Due date (YYYY-MM-DD) |
| `Comments` | string | No | Document comments |
| `DocumentLines` | array | Yes | Array of line items (minimum 1) |

**Note:** `BPL_IDAssignedToInvoice` is required when SAP B1 has multi-branch enabled.

### Document Line Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ItemCode` | string | Yes | Item code |
| `Quantity` | decimal | Yes | Quantity received |
| `TaxCode` | string | No | Tax code |
| `UnitPrice` | decimal | No | Unit price |
| `WarehouseCode` | string | No | Target warehouse code |
| `BaseEntry` | integer | No | Base PO DocEntry (for PO-based GRPO) |
| `BaseLine` | integer | No | Base PO line number (0-indexed) |
| `BaseType` | integer | No | Base document type (22 = Purchase Order) |

## Response

### Success (201 Created)

```json
{
    "DocEntry": 123,
    "DocNum": 456,
    "CardCode": "V001",
    "CardName": "Vendor Name Pvt Ltd",
    "DocDate": "2026-02-02",
    "DocTotal": 8750.00
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `DocEntry` | integer | Internal document entry ID |
| `DocNum` | integer | Document number |
| `CardCode` | string | Supplier code |
| `CardName` | string | Supplier name |
| `DocDate` | string | Document date |
| `DocTotal` | decimal | Total document amount |

## Error Responses

### 400 Bad Request - Validation Error

```json
{
    "detail": "Invalid request data",
    "errors": {
        "CardCode": ["This field is required."],
        "DocumentLines": ["At least one document line is required"]
    }
}
```

### 400 Bad Request - SAP Validation Error

```json
{
    "detail": "Item 'ITEM001' does not exist [OITM]"
}
```

### 401 Unauthorized

```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden

```json
{
    "detail": "Company-Code header is missing."
}
```

### 502 Bad Gateway - SAP Error

```json
{
    "detail": "Failed to create GRPO: <SAP error message>"
}
```

### 503 Service Unavailable

```json
{
    "detail": "SAP system is currently unavailable. Please try again later."
}
```

## Multi-Company Support

The API automatically routes requests to the correct SAP company database based on the `Company-Code` header.

| Company Code | SAP Database |
|--------------|--------------|
| `JIVO_OIL` | TEST_OIL_15122025 |
| `JIVO_MART` | JIVO_MART_DB |

## Code Example

### Python (requests)

```python
import requests

url = "https://your-server/api/v1/po/grpo/"
headers = {
    "Authorization": "Bearer <your_access_token>",
    "Company-Code": "JIVO_OIL",
    "Content-Type": "application/json"
}
payload = {
    "CardCode": "V001",
    "DocumentLines": [
        {
            "ItemCode": "ITEM001",
            "Quantity": "100",
            "TaxCode": "T1",
            "UnitPrice": "50"
        }
    ]
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

### cURL

```bash
curl -X POST https://your-server/api/v1/po/grpo/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Company-Code: JIVO_OIL" \
  -H "Content-Type: application/json" \
  -d '{
    "CardCode": "V001",
    "DocumentLines": [
      {
        "ItemCode": "ITEM001",
        "Quantity": "100",
        "TaxCode": "T1",
        "UnitPrice": "50"
      }
    ]
  }'
```

## Related Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/sap/open-pos/` | GET | Get open purchase orders |
| `/api/v1/sap/open-pos/<po_number>/items/` | GET | Get PO line items |
