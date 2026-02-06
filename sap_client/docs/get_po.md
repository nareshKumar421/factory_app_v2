# Get Purchase Orders (PO) API

This document describes how to retrieve Purchase Orders from SAP B1 using the SAP Client APIs.

## Endpoints

### 1. Get Open POs List

Retrieves a list of open Purchase Orders for a specific supplier.

**Endpoint:** `GET /api/sap/open-pos/`

**Authentication:** Required (JWT Token)

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| supplier_code | string | Yes | The supplier/vendor code in SAP |

**Example Request:**
```bash
curl -X GET "http://your-domain.com/api/sap/open-pos/?supplier_code=V001" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json"
```

**Success Response (200 OK):**
```json
[
  {
    "po_number": "PO-00001",
    "supplier_code": "V001",
    "supplier_name": "ABC Suppliers Ltd",
    "items": [
      {
        "po_item_code": "ITEM001",
        "item_name": "Raw Material A",
        "ordered_qty": 1000.000,
        "received_qty": 500.000,
        "remaining_qty": 500.000,
        "uom": "KG"
      },
      {
        "po_item_code": "ITEM002",
        "item_name": "Raw Material B",
        "ordered_qty": 200.000,
        "received_qty": 0.000,
        "remaining_qty": 200.000,
        "uom": "PCS"
      }
    ]
  }
]
```

**Error Responses:**

| Status Code | Description |
|-------------|-------------|
| 400 Bad Request | supplier_code is missing |
| 401 Unauthorized | Invalid or missing authentication token |
| 502 Bad Gateway | Failed to retrieve data from SAP |
| 503 Service Unavailable | SAP system is currently unavailable |

---

### 2. Get PO Items by PO Number

Retrieves details and items for a specific Purchase Order.

**Endpoint:** `GET /api/sap/open-pos/<po_number>/items/`

**Authentication:** Required (JWT Token)

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| po_number | string | Yes | The Purchase Order number |

**Example Request:**
```bash
curl -X GET "http://your-domain.com/api/sap/open-pos/PO-00001/items/" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json"
```

**Success Response (200 OK):**
```json
{
  "po_number": "PO-00001",
  "supplier_code": "V001",
  "supplier_name": "ABC Suppliers Ltd",
  "items": [
    {
      "po_item_code": "ITEM001",
      "item_name": "Raw Material A",
      "ordered_qty": 1000.000,
      "received_qty": 500.000,
      "remaining_qty": 500.000,
      "uom": "KG"
    },
    {
      "po_item_code": "ITEM002",
      "item_name": "Raw Material B",
      "ordered_qty": 200.000,
      "received_qty": 0.000,
      "remaining_qty": 200.000,
      "uom": "PCS"
    }
  ]
}
```

**Error Responses:**

| Status Code | Description |
|-------------|-------------|
| 401 Unauthorized | Invalid or missing authentication token |
| 404 Not Found | PO not found |
| 502 Bad Gateway | Failed to retrieve data from SAP |
| 503 Service Unavailable | SAP system is currently unavailable |

---

## Response Fields

### PO Object

| Field | Type | Description |
|-------|------|-------------|
| po_number | string | Purchase Order number |
| supplier_code | string | Supplier/Vendor code |
| supplier_name | string | Supplier/Vendor name |
| items | array | List of PO line items |

### PO Item Object

| Field | Type | Description |
|-------|------|-------------|
| po_item_code | string | Item code |
| item_name | string | Item description/name |
| ordered_qty | decimal | Total quantity ordered |
| received_qty | decimal | Quantity already received |
| remaining_qty | decimal | Remaining quantity to receive |
| uom | string | Unit of measure |

---

## Usage Notes

1. **Company Context:** The API uses the authenticated user's company context to connect to the correct SAP instance.

2. **Open POs Only:** These endpoints return only open Purchase Orders (not fully received or closed).

3. **Remaining Quantity:** Use the `remaining_qty` field to determine how much can still be received against each PO line.
