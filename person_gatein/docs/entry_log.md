# EntryLog Table Documentation

## Purpose
The `EntryLog` table tracks the entry and exit of **Visitors** and **Labours** through factory gates. It's the core table for gate-in/gate-out management.

---

## Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `person_type` | FK → PersonType | **Yes** | Type of person: "Visitor" or "Labour" |
| `visitor` | FK → Visitor | Conditional | Required if person_type is Visitor |
| `labour` | FK → Labour | Conditional | Required if person_type is Labour |
| `name_snapshot` | CharField | **Auto-filled** | Copied from visitor/labour name at entry time (audit trail) |
| `photo_snapshot` | ImageField | Optional | Photo captured at entry time |
| `gate_in` | FK → Gate | **Yes** | Gate where person entered |
| `gate_out` | FK → Gate | On exit | Gate where person exited (filled during exit) |
| `entry_time` | DateTime | **Auto** | Auto-set when record created |
| `exit_time` | DateTime | On exit | Set when person exits |
| `purpose` | CharField | Optional | Reason for visit |
| `approved_by` | FK → User | Optional | Who approved this entry |
| `vehicle_no` | CharField | Optional | Vehicle number if applicable |
| `remarks` | TextField | Optional | Additional notes |
| `status` | Choice | **Auto** | "IN" / "OUT" / "CANCELLED" |
| `created_by` | FK → User | **Auto** | User who created the entry |
| `created_at` | DateTime | **Auto** | Record creation timestamp |
| `updated_at` | DateTime | **Auto** | Last update timestamp |

---

## Status Values

| Status | Meaning |
|--------|---------|
| `IN` | Person is currently inside the premises |
| `OUT` | Person has exited |
| `CANCELLED` | Entry was cancelled/voided |

---

## Example Payloads

### 1. Visitor Entry (Check-in)
```json
{
    "person_type": 1,
    "visitor": 5,
    "gate_in": 1,
    "purpose": "Meeting with HR Department",
    "approved_by": 2,
    "vehicle_no": "MH12AB1234",
    "remarks": "Scheduled interview candidate"
}
```
**Auto-filled by system:** `name_snapshot`, `entry_time`, `status="IN"`, `created_by`, `created_at`

---

### 2. Labour Entry (Check-in)
```json
{
    "person_type": 2,
    "labour": 10,
    "gate_in": 2,
    "purpose": "Construction work - Building A",
    "remarks": "Safety gear verified"
}
```

---

### 3. Visitor Entry (Minimal - Walk-in)
```json
{
    "person_type": 1,
    "visitor": 8,
    "gate_in": 1
}
```

---

### 4. Exit (Check-out)
Call the exit endpoint with:
```json
{
    "entry_id": 15,
    "gate_out_id": 2
}
```
**System updates:** `status="OUT"`, `exit_time`, `gate_out`

---

## When to Fill Each Field

| Scenario | Fields to Provide |
|----------|-------------------|
| **Visitor check-in** | `person_type`, `visitor`, `gate_in`, optionally `purpose`, `approved_by`, `vehicle_no`, `remarks` |
| **Labour check-in** | `person_type`, `labour`, `gate_in`, optionally `purpose`, `remarks` |
| **Check-out** | Only `entry_id` and optionally `gate_out_id` (via exit API) |
| **With vehicle** | Add `vehicle_no` |
| **Pre-approved visit** | Add `approved_by` (user ID who approved) |
| **Capture photo at gate** | Add `photo_snapshot` (image file) |

---

## Business Rules

1. **Mutual exclusivity**: Either `visitor` OR `labour` must be provided, never both
2. **No double entry**: A person already with status "IN" cannot enter again
3. **Snapshot for audit**: `name_snapshot` is auto-copied so even if visitor/labour record changes, the entry log preserves the original name
4. **Exit requires IN status**: Can only exit if current status is "IN"
