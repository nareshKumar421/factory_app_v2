# Get Active Warehouses API

This document describes how to retrieve all active warehouses from SAP B1 using the SAP Client API.

## Endpoint

**URL:** `GET /api/v1/po/warehouses/`

**Authentication:** Required (JWT Token)

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Company-Code: <company_code>
Content-Type: application/json
```

---

## Request

No query parameters or request body required.

**Example Request:**
```bash
curl -X GET "http://your-domain.com/api/v1/po/warehouses/" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Company-Code: JIVO_OIL" \
  -H "Content-Type: application/json"
```

---

## Response

### Success Response (200 OK)

```json
[
  {
    "warehouse_code": "WH01",
    "warehouse_name": "Main Warehouse"
  },
  {
    "warehouse_code": "WH02",
    "warehouse_name": "Raw Material Store"
  },
  {
    "warehouse_code": "WH03",
    "warehouse_name": "Finished Goods Warehouse"
  }
]
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| warehouse_code | string | Warehouse code in SAP (WhsCode) |
| warehouse_name | string | Warehouse name/description (WhsName) |

---

## Error Responses

| Status Code | Description |
|-------------|-------------|
| 401 Unauthorized | Invalid or missing authentication token |
| 403 Forbidden | Company-Code header is missing or user does not have access |
| 502 Bad Gateway | Failed to retrieve warehouse data from SAP |
| 503 Service Unavailable | SAP system is currently unavailable |

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

### 502 Bad Gateway

```json
{
  "detail": "Failed to retrieve warehouse data from SAP."
}
```

### 503 Service Unavailable

```json
{
  "detail": "SAP system is currently unavailable. Please try again later."
}
```

---

## SAP Source

This API queries the SAP HANA `OWHS` (Warehouses) table, filtering for active warehouses only (`Inactive = 'N'`). Results are ordered by warehouse code.

---

## Code Example

### Python (requests)

```python
import requests

url = "https://your-server/api/v1/po/warehouses/"
headers = {
    "Authorization": "Bearer <your_access_token>",
    "Company-Code": "JIVO_OIL",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
warehouses = response.json()

for wh in warehouses:
    print(f"{wh['warehouse_code']} - {wh['warehouse_name']}")
```

### cURL

```bash
curl -X GET https://your-server/api/v1/po/warehouses/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Company-Code: JIVO_OIL" \
  -H "Content-Type: application/json"
```

---

## Usage Notes

1. **Company Context:** The API uses the `Company-Code` header to connect to the correct SAP instance.

2. **Active Only:** Only active warehouses are returned. Inactive warehouses (marked as `Inactive = 'Y'` in SAP) are excluded.

3. **Ordering:** Results are sorted alphabetically by warehouse code.

4. **Use Case:** This endpoint is useful for populating warehouse dropdowns in the GRPO creation form, where the `WarehouseCode` field needs a valid warehouse.

---

## Related Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/po/open-pos/` | GET | Get open purchase orders |
| `/api/v1/po/open-pos/<po_number>/items/` | GET | Get PO line items |
| `/api/v1/po/grpo/` | POST | Create GRPO in SAP |
