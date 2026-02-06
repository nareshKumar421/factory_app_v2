# GRPO Error Codes and Troubleshooting

This document lists all error codes and messages that can be returned by the GRPO API.

## HTTP Status Codes

| Status | Meaning |
|--------|---------|
| 200 | Success - Request completed |
| 201 | Created - GRPO posted successfully |
| 400 | Bad Request - Invalid input or business rule violation |
| 401 | Unauthorized - Missing or invalid authentication |
| 404 | Not Found - Resource doesn't exist |
| 502 | Bad Gateway - SAP error |
| 503 | Service Unavailable - SAP system down |

---

## Error Categories

### 1. Authentication Errors (401)

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Authentication credentials were not provided" | No token in header | Add `Authorization: Bearer <token>` |
| "Given token not valid for any token type" | Token expired/invalid | Get a new token from login API |
| "User is not authenticated" | Authentication failed | Re-authenticate |

**Example Response:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### 2. Validation Errors (400)

#### Missing Required Fields

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "vehicle_entry_id is required" | Missing field | Add vehicle_entry_id to request |
| "po_receipt_id is required" | Missing field | Add po_receipt_id to request |

**Example Response:**
```json
{
  "detail": "Invalid request data",
  "errors": {
    "po_receipt_id": ["This field is required."]
  }
}
```

#### Business Rule Violations

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Vehicle entry {id} not found" | Invalid vehicle_entry_id | Verify the ID exists |
| "PO receipt {id} not found for this vehicle entry" | Invalid po_receipt_id | Verify PO belongs to the entry |
| "Gate entry is not completed. Current status: {status}" | Entry not ready | Complete gate entry first |
| "GRPO already posted for PO {number}. SAP Doc Num: {num}" | Duplicate posting | No action needed - already done |
| "No accepted quantities to post for this PO" | All items rejected | No GRPO needed |

**Example Response:**
```json
{
  "detail": "Gate entry is not completed. Current status: IN_PROGRESS"
}
```

---

### 3. SAP Errors

#### SAP Validation Errors (400)

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "SAP validation error: {details}" | SAP rejected the data | Check SAP validation rules |
| "Item {code} is not active in SAP" | Item deactivated | Activate item in SAP |
| "Supplier {code} is not authorized" | Supplier issue | Check supplier status in SAP |
| "Quantity exceeds open PO quantity" | Over-receipt | Verify quantities |

**Example Response:**
```json
{
  "detail": "SAP validation error: Item ITEM001 is not active in SAP"
}
```

#### SAP Connection Errors (503)

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "SAP system is currently unavailable. Please try again later." | SAP Service Layer down | Wait and retry |

**Example Response:**
```json
{
  "detail": "SAP system is currently unavailable. Please try again later."
}
```

#### SAP Data Errors (502)

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "SAP error: {details}" | SAP internal error | Check SAP logs |
| "Failed to create GRPO in SAP" | General SAP failure | Check SAP connection and logs |

**Example Response:**
```json
{
  "detail": "SAP error: Failed to create document"
}
```

---

### 4. Not Found Errors (404)

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "GRPO posting not found" | Invalid posting ID | Verify the posting ID |
| "Vehicle entry not found" | Invalid entry ID | Verify the entry ID |

**Example Response:**
```json
{
  "detail": "GRPO posting not found"
}
```

---

## Troubleshooting Guide

### Problem: "Gate entry is not completed"

**Symptoms:**
- GRPO posting fails with status 400
- Error mentions entry status

**Diagnosis:**
1. Check entry status: `GET /api/v1/grpo/preview/{id}/`
2. Look at `entry_status` field

**Resolution:**
1. Complete security check if pending
2. Complete weighment if pending
3. Submit arrival slips for all items
4. Complete QC inspections
5. Call gate completion API

---

### Problem: "No accepted quantities"

**Symptoms:**
- GRPO posting fails
- All items have 0 accepted_qty

**Diagnosis:**
1. Preview GRPO data
2. Check `accepted_qty` for each item

**Resolution:**
1. This is expected if QC rejected all items
2. No GRPO is needed - goods are rejected
3. Handle rejected goods through returns process

---

### Problem: "SAP system unavailable"

**Symptoms:**
- 503 error
- Cannot post any GRPO

**Diagnosis:**
1. Check SAP Service Layer status
2. Check network connectivity
3. Verify SAP credentials

**Resolution:**
1. Wait for SAP to come online
2. Contact SAP administrator
3. Retry posting after SAP is available

---

### Problem: "GRPO already posted"

**Symptoms:**
- 400 error when posting
- Message shows existing SAP Doc Num

**Diagnosis:**
- GRPO was already successfully posted

**Resolution:**
1. No action needed
2. Check posting history for details
3. Use provided SAP Doc Num for reference

---

## Error Logging

All errors are logged with:
- Timestamp
- User ID
- Request details
- Full error message
- Stack trace (for server errors)

**Log location:** Check Django logs at configured location

**Log format:**
```
2024-01-15 14:30:00 ERROR grpo.services: SAP validation error posting GRPO: Item ITEM001 is not active
```

---

## Support Escalation

If issue persists after troubleshooting:

1. **Collect Information:**
   - Error message and status code
   - Request payload
   - Vehicle entry ID and PO number
   - Timestamp of error

2. **Check Logs:**
   - Application logs
   - SAP Service Layer logs
   - Network logs (if connectivity issue)

3. **Escalate To:**
   - Level 1: Application support team
   - Level 2: SAP integration team
   - Level 3: SAP administrator
