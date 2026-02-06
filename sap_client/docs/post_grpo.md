# Create GRPO (Goods Receipt PO) API

This document describes how to create a Goods Receipt Purchase Order (GRPO) in SAP B1.

## Endpoint

**URL:** `POST /api/sap/grpo/`

**Authentication:** Required (JWT Token)

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

---

## Request Payload

### Full Payload Structure

```json
{
  "CardCode": "V001",
  "BPL_IDAssignedToInvoice": 1,
  "DocDate": "2024-01-15",
  "DocDueDate": "2024-01-20",
  "Comments": "Goods received against PO-00001",
  "DocumentLines": [
    {
      "ItemCode": "ITEM001",
      "Quantity": 100.000,
      "TaxCode": "T1",
      "UnitPrice": 50.00,
      "WarehouseCode": "WH01",
      "BaseEntry": 123,
      "BaseLine": 0,
      "BaseType": 22
    }
  ]
}
```

### Request Fields

#### Header Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| CardCode | string | Yes | Supplier/Vendor code in SAP |
| BPL_IDAssignedToInvoice | integer | No | Branch/Business Place ID |
| DocDate | date | No | Document date (YYYY-MM-DD format) |
| DocDueDate | date | No | Document due date (YYYY-MM-DD format) |
| Comments | string | No | Comments or remarks |
| DocumentLines | array | Yes | Array of line items (minimum 1 required) |

#### Document Line Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| ItemCode | string | Yes | Item code in SAP |
| Quantity | decimal | Yes | Quantity being received |
| TaxCode | string | No | Tax code (e.g., "T1", "GST18") |
| UnitPrice | decimal | No | Unit price |
| WarehouseCode | string | No | Target warehouse code |
| BaseEntry | integer | No | Base PO document entry (DocEntry) |
| BaseLine | integer | No | Base PO line number (0-indexed) |
| BaseType | integer | No | Base document type (22 = Purchase Order) |

---

## Example Requests

### Basic GRPO (Without PO Reference)

Create a standalone GRPO without linking to a Purchase Order.

```bash
curl -X POST "http://your-domain.com/api/sap/grpo/" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "CardCode": "V001",
    "DocumentLines": [
      {
        "ItemCode": "ITEM001",
        "Quantity": 100,
        "TaxCode": "T1",
        "UnitPrice": 50
      }
    ]
  }'
```

### GRPO Linked to Purchase Order

Create a GRPO that references an existing Purchase Order. This will update the received quantity on the PO.

```bash
curl -X POST "http://your-domain.com/api/sap/grpo/" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "CardCode": "V001",
    "DocDate": "2024-01-15",
    "Comments": "Partial delivery received",
    "DocumentLines": [
      {
        "ItemCode": "ITEM001",
        "Quantity": 500,
        "WarehouseCode": "WH01",
        "BaseEntry": 123,
        "BaseLine": 0,
        "BaseType": 22
      },
      {
        "ItemCode": "ITEM002",
        "Quantity": 100,
        "WarehouseCode": "WH01",
        "BaseEntry": 123,
        "BaseLine": 1,
        "BaseType": 22
      }
    ]
  }'
```

### GRPO with Multiple Items

```bash
curl -X POST "http://your-domain.com/api/sap/grpo/" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "CardCode": "V001",
    "BPL_IDAssignedToInvoice": 1,
    "DocDate": "2024-01-15",
    "DocDueDate": "2024-01-30",
    "Comments": "Bulk material receipt",
    "DocumentLines": [
      {
        "ItemCode": "RM001",
        "Quantity": 1000,
        "TaxCode": "GST18",
        "UnitPrice": 25.50,
        "WarehouseCode": "RAW-WH"
      },
      {
        "ItemCode": "RM002",
        "Quantity": 500,
        "TaxCode": "GST18",
        "UnitPrice": 100.00,
        "WarehouseCode": "RAW-WH"
      },
      {
        "ItemCode": "RM003",
        "Quantity": 250,
        "TaxCode": "GST5",
        "UnitPrice": 75.00,
        "WarehouseCode": "RAW-WH"
      }
    ]
  }'
```

---

## Response

### Success Response (201 Created)

```json
{
  "DocEntry": 456,
  "DocNum": 1001,
  "CardCode": "V001",
  "CardName": "ABC Suppliers Ltd",
  "DocDate": "2024-01-15",
  "DocTotal": 5000.00
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| DocEntry | integer | Internal document entry ID in SAP |
| DocNum | integer | Document number (visible in SAP UI) |
| CardCode | string | Supplier code |
| CardName | string | Supplier name |
| DocDate | string | Document date |
| DocTotal | decimal | Total document value |

---

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
  "detail": "Item ITEM001 is not active in SAP"
}
```

### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 502 Bad Gateway

```json
{
  "detail": "Failed to create GRPO in SAP"
}
```

### 503 Service Unavailable

```json
{
  "detail": "SAP system is currently unavailable. Please try again later."
}
```

---

## Important Notes

1. **Company Context:** The API automatically uses the authenticated user's company context to connect to the correct SAP B1 instance.

2. **PO Linking:** When linking to a Purchase Order:
   - Use `BaseEntry` (the PO's DocEntry, not DocNum)
   - Use `BaseLine` (0-indexed line number)
   - Set `BaseType` to 22 (Purchase Order document type)

3. **Quantity Validation:** When linked to a PO, the quantity cannot exceed the remaining quantity on the PO line.

4. **Warehouse:** If `WarehouseCode` is not provided, SAP will use the default warehouse for the item.

5. **Tax Calculation:** If `TaxCode` is provided, SAP will automatically calculate the tax based on the configured tax rates.

6. **Document Dates:** If `DocDate` is not provided, SAP will use the current date.

---

## Workflow Example

### Receiving Goods Against a Purchase Order

1. **Get Open POs for Supplier:**
   ```
   GET /api/sap/open-pos/?supplier_code=V001
   ```

2. **Get PO Details:**
   ```
   GET /api/sap/open-pos/PO-00001/items/
   ```

3. **Create GRPO:**
   ```
   POST /api/sap/grpo/
   {
     "CardCode": "V001",
     "DocumentLines": [
       {
         "ItemCode": "ITEM001",
         "Quantity": 500,
         "BaseEntry": 123,
         "BaseLine": 0,
         "BaseType": 22
       }
     ]
   }
   ```

4. **Verify Remaining Quantity:**
   ```
   GET /api/sap/open-pos/PO-00001/items/
   ```
   The `remaining_qty` should now reflect the received quantity.
