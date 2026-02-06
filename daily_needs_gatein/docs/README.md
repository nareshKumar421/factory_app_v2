Perfect 👍
I’ll now lay this out **step-by-step**, exactly like we did for **Raw Material**, but **tailored for Daily Need & Canteen**, and **aligned with everything we already decided**.

No assumptions.
No QC.
No Weighment.
Separate completion.
Parent gate lock respected.

---

# 🏭 DAILY NEED & CANTEEN — STEP-BY-STEP FLOW

This is the **FULL USER + API FLOW**, from vehicle arrival to gate lock.

---

## 🔑 PRE-CONDITION (COMMON FOR ALL FLOWS)

These already exist (same as Raw Material):

* Driver master
* Vehicle master
* Security module
* VehicleEntry table
* `VehicleEntry.entry_type = "DAILY_NEED"`

---

# ✅ STEP 1 — VEHICLE ARRIVES (CREATE VEHICLE ENTRY)

### 👤 User: Gate Security

### API

```
POST /api/v1/vehicle-entries/
```

### Payload

```json
{
  "entry_no": "GE-2026-0105",
  "vehicle": 12,
  "driver": 7,
  "entry_type": "DAILY_NEED",
  "remarks": "Canteen vegetables"
}
```

### Result

* `VehicleEntry` created
* `status = DRAFT`
* `is_locked = false`

📌 Meaning:

> Truck registered, nothing started yet

---

# ✅ STEP 2 — SECURITY CHECK STARTS (STATUS CHANGE)

### 👤 User: Security Guard

### API

```
POST /api/v1/gate-entries/{gate_entry_id}/security/
```

### Payload

```json
{
  "vehicle_condition_ok": true,
  "tyre_condition_ok": true,
  "alcohol_test_done": true,
  "alcohol_test_passed": true,
  "remarks": "All OK"
}
```

### System Action

* SecurityCheck created
* 🔁 `status: DRAFT → IN_PROGRESS`

📌 Meaning:

> Gate process officially started

---

# ✅ STEP 3 — SECURITY SUBMIT (LOCK SECURITY ONLY)

### 👤 User: Security Supervisor

### API

```
POST /api/v1/security/{security_id}/submit/
```

### Payload

```json
{}
```

### Result

* Security locked
* `VehicleEntry` still editable
* `status = IN_PROGRESS`

📌 Meaning:

> Security done, move to material details

---

# ✅ STEP 4 — DAILY NEED / CANTEEN ENTRY (MAIN STEP)

### 👤 User: Store / Canteen In-charge

### API

```
POST /api/v1/gate-entries/{gate_entry_id}/daily-need/
```

### Payload (matches your UI)

```json
{
  "item_category": "CANTEEN",
  "supplier_name": "Fresh Veg Supplier",
  "material_name": "Vegetables",
  "quantity": 50,
  "unit": "KG",
  "receiving_department": "Canteen",
  "bill_number": "BILL-4587",
  "delivery_challan_number": "DC-4587",
  "canteen_supervisor": "Ramesh",
  "vehicle_or_person_name": "Tempo DL01AB2233",
  "contact_number": "9876543210",
  "remarks": "Morning supply"
}
```

### Validations

✔ Gate not locked
✔ Entry type = `DAILY_NEED`
✔ Only one daily-need entry allowed

### Result

* `DailyNeedGateEntry` created
* `VehicleEntry.status` stays `IN_PROGRESS`

📌 Meaning:

> Daily need details captured

---

# ❌ WHAT DOES NOT HAPPEN HERE (IMPORTANT)

* ❌ No QC
* ❌ No Weighment
* ❌ No PO
* ❌ No SAP

This is **intentional**.

---

# ✅ STEP 5 — DAILY NEED COMPLETION (SEPARATE FUNCTION)

### 👤 User: Gate Supervisor

### API

```
POST /api/v1/gate-entries/{gate_entry_id}/daily-need/complete/
```

### Internally calls

```python
complete_daily_need_gate_entry(vehicle_entry)
```

### Validations performed

✔ Entry type = `DAILY_NEED`
✔ Security check exists
✔ Daily need entry exists
❌ No QC check
❌ No Weighment check

### System Action

* `VehicleEntry.status = COMPLETED`
* `VehicleEntry.is_locked = true`

📌 Meaning:

> Vehicle cleared, gate closed

---

# 🔒 STEP 6 — POST-COMPLETION BEHAVIOR

After completion:

| Action           | Allowed? |
| ---------------- | -------- |
| Edit daily need  | ❌        |
| Edit security    | ❌        |
| Add weighment    | ❌        |
| Add raw material | ❌        |
| Re-open gate     | ❌        |

Everything is locked by **parent VehicleEntry**.

---

# 🧠 FULL STATUS TIMELINE (DAILY NEED)

```
Create Entry        → DRAFT
Security starts     → IN_PROGRESS
Daily Need filled   → IN_PROGRESS
Daily Need complete → COMPLETED 🔒
```

---

# 🧠 WHY THIS FLOW IS CORRECT

✔ Matches your UI (single page)
✔ No unnecessary validations
✔ Separate completion avoids errors
✔ One gate = one lock
✔ Extendable to Maintenance / Construction

---

# 🏁 FINAL ONE-LINE SUMMARY

> **Daily Need & Canteen uses the same gate,
> but its own rules to close that gate.**

---

If you want next, I can:

* Create **GET Daily Need entry API**
* Merge Daily Need into **full gate summary**
* Create **Maintenance flow same way**
* Add **role-based permissions**
* Draw **combined Raw + Daily flow diagram**

Just tell me 👍
