# Get Active Vendors API

This document describes how to retrieve all active vendors (suppliers) from SAP B1 using the SAP Client API.

## Endpoint

**URL:** `GET /api/v1/po/vendors/`

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
curl -X GET "http://your-domain.com/api/v1/po/vendors/" \
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
    "vendor_code": "V001",
    "vendor_name": "ABC Suppliers Pvt Ltd"
  },
  {
    "vendor_code": "V002",
    "vendor_name": "XYZ Raw Materials Ltd"
  },
  {
    "vendor_code": "V003",
    "vendor_name": "Global Trading Co."
  }
]
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| vendor_code | string | Vendor/Supplier code in SAP (CardCode) |
| vendor_name | string | Vendor/Supplier name (CardName) |

---

## Error Responses

| Status Code | Description |
|-------------|-------------|
| 401 Unauthorized | Invalid or missing authentication token |
| 403 Forbidden | Company-Code header is missing or user does not have access |
| 502 Bad Gateway | Failed to retrieve vendor data from SAP |
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
  "detail": "Failed to retrieve vendor data from SAP."
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

This API queries the SAP HANA `OCRD` (Business Partners) table with the following filters:
- `CardType = 'S'` — Suppliers/Vendors only
- `frozenFor = 'N'` — Active (not frozen) vendors only

Results are ordered by vendor name.

---

## Code Example

### Python (requests)

```python
import requests

url = "https://your-server/api/v1/po/vendors/"
headers = {
    "Authorization": "Bearer <your_access_token>",
    "Company-Code": "JIVO_OIL",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
vendors = response.json()

for v in vendors:
    print(f"{v['vendor_code']} - {v['vendor_name']}")
```

### cURL

```bash
curl -X GET https://your-server/api/v1/po/vendors/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Company-Code: JIVO_OIL" \
  -H "Content-Type: application/json"
```

---

## Usage Notes

1. **Company Context:** The API uses the `Company-Code` header to connect to the correct SAP instance.

2. **Active Only:** Only active vendors are returned. Frozen vendors (`frozenFor = 'Y'` in SAP) are excluded.

3. **Suppliers Only:** Only business partners with `CardType = 'S'` (Supplier) are returned. Customers and leads are excluded.

4. **Use Case:** This endpoint is useful for populating vendor/supplier dropdowns when creating POs or GRPOs.

---

## Related Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/po/open-pos/` | GET | Get open purchase orders for a supplier |
| `/api/v1/po/open-pos/<po_number>/items/` | GET | Get PO line items |
| `/api/v1/po/warehouses/` | GET | Get active warehouses |
| `/api/v1/po/grpo/` | POST | Create GRPO in SAP |
