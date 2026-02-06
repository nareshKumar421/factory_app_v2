# GRPO API Documentation

## Base URL
```
/api/grpo/
```

## Headers Required
```
Authorization: Bearer <access_token>
Company-Code: <company_code>
```

---

## Endpoints

### 1. Pending GRPO List

List completed gate entries pending GRPO posting.

```
GET /api/grpo/pending/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `grpo.can_view_pending_grpo`

**Response (200 OK):**
```json
[
    {
        "vehicle_entry_id": 123,
        "entry_no": "GE-2026-001",
        "status": "COMPLETED",
        "entry_time": "2026-02-01T10:00:00Z",
        "total_po_count": 3,
        "posted_po_count": 1,
        "pending_po_count": 2,
        "is_fully_posted": false
    }
]
```

---

### 2. GRPO Preview

Preview all data required for GRPO posting for a specific gate entry.

```
GET /api/grpo/preview/{vehicle_entry_id}/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `grpo.can_preview_grpo`

**Response (200 OK):** PO details, items, QC status, and accepted quantities.

**Error Response (404):**
```json
{
    "detail": "Vehicle entry not found"
}
```

---

### 3. Post GRPO

Post GRPO to SAP for a specific PO receipt.

```
POST /api/grpo/post/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `grpo.can_create_grpo_posting`

**Request Body:**
```json
{
    "vehicle_entry_id": 123,
    "po_receipt_id": 456,
    "items": [
        {"po_item_receipt_id": 1, "accepted_qty": 100.5},
        {"po_item_receipt_id": 2, "accepted_qty": 50.0}
    ],
    "branch_id": 1,
    "warehouse_code": "WH01",
    "comments": "Gate entry completed"
}
```

**Response (201 Created):**
```json
{
    "success": true,
    "grpo_posting_id": 1,
    "sap_doc_entry": 12345,
    "sap_doc_num": 67890,
    "sap_doc_total": "1500.00",
    "message": "GRPO posted successfully. SAP Doc Num: 67890"
}
```

**Error Responses:**

| Status | Message |
|--------|---------|
| 400 | `Invalid request data` |
| 400 | `SAP validation error: ...` |
| 403 | `You do not have permission to perform this action.` |
| 502 | `SAP error: ...` |
| 503 | `SAP system is currently unavailable. Please try again later.` |

---

### 4. GRPO Posting History

View GRPO posting history, optionally filtered by vehicle entry.

```
GET /api/grpo/history/
GET /api/grpo/history/?vehicle_entry_id=123
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `grpo.can_view_grpo_history`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `vehicle_entry_id` | integer | No | Filter by vehicle entry ID |

---

### 5. GRPO Posting Detail

View details of a specific GRPO posting.

```
GET /api/grpo/{posting_id}/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `grpo.can_view_grpo_posting`

**Error Response (404):**
```json
{
    "detail": "GRPO posting not found"
}
```

---

## Permission Summary

| Endpoint | Method | Permission Codename |
|----------|--------|---------------------|
| `/pending/` | GET | `can_view_pending_grpo` |
| `/preview/{id}/` | GET | `can_preview_grpo` |
| `/post/` | POST | `can_create_grpo_posting` |
| `/history/` | GET | `can_view_grpo_history` |
| `/{posting_id}/` | GET | `can_view_grpo_posting` |

## All Permissions

| Permission Codename | Description |
|---------------------|-------------|
| `grpo.can_view_grpo_posting` | Can view GRPO posting |
| `grpo.can_create_grpo_posting` | Can create GRPO posting |
| `grpo.can_view_pending_grpo` | Can view pending GRPO entries |
| `grpo.can_preview_grpo` | Can preview GRPO data |
| `grpo.can_view_grpo_history` | Can view GRPO posting history |

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
