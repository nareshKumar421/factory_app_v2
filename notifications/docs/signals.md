# Notifications - Signals Documentation

Signals auto-trigger push notifications when key events happen in the system. All signals are registered in `notifications/apps.py` via `ready()`.

---

## Signal Registration

**File:** `notifications/signals.py`
**Connected in:** `notifications/apps.py` -> `NotificationsConfig.ready()`

All signals use `post_save` with string-based sender references to avoid circular imports.

---

## Signal List

### 1. Gate Entry Created

| Property     | Value                              |
|--------------|------------------------------------|
| Signal       | `post_save`                        |
| Sender       | `driver_management.VehicleEntry`   |
| Fires when   | New VehicleEntry is created (`created=True`) |
| Type         | `GATE_ENTRY_CREATED`               |
| Recipients   | All active users in the same company, excluding the creator |
| Deep link    | `/gate-entries/{entry_id}`         |

**Notification content:**
- Title: `"New Gate Entry Created"`
- Body: `"Gate entry {entry_no} ({entry_type}) has been created."`

---

### 2. Weighment Recorded

| Property     | Value                              |
|--------------|------------------------------------|
| Signal       | `post_save`                        |
| Sender       | `weighment.Weighment`              |
| Fires when   | New Weighment is created (`created=True`) |
| Type         | `WEIGHMENT_RECORDED`               |
| Recipients   | All active users in the same company, excluding the creator |
| Deep link    | `/gate-entries/{entry_id}`         |

**Notification content:**
- Title: `"Weighment Recorded"`
- Body: `"Weighment recorded for {entry_no}. Net: {net_weight} kg."`

---

### 3. Arrival Slip Submitted

| Property     | Value                                    |
|--------------|------------------------------------------|
| Signal       | `post_save`                              |
| Sender       | `quality_control.MaterialArrivalSlip`    |
| Fires when   | `is_submitted=True` AND `status="SUBMITTED"` |
| Type         | `ARRIVAL_SLIP_SUBMITTED`                 |
| Recipients   | All active users in the same company, excluding the submitter |
| Deep link    | `/gate-entries/{entry_id}/qc`            |

**Notification content:**
- Title: `"Arrival Slip Submitted"`
- Body: `"Arrival slip for {item_name} submitted for QC."`

---

### 4. QC Inspection Workflow

| Property     | Value                                      |
|--------------|--------------------------------------------|
| Signal       | `post_save`                                |
| Sender       | `quality_control.RawMaterialInspection`    |
| Fires when   | `workflow_status` matches one of the statuses below |
| Recipients   | All active users in the same company       |

**Status-specific behavior:**

| `workflow_status`       | Notification Type            | Title                       |
|-------------------------|------------------------------|-----------------------------|
| `SUBMITTED`             | `QC_INSPECTION_SUBMITTED`    | "QC Inspection Submitted"   |
| `QA_CHEMIST_APPROVED`   | `QC_CHEMIST_APPROVED`        | "QC Chemist Approved"       |
| `QAM_APPROVED`          | `QC_QAM_APPROVED`            | "QAM Approved"              |

**Deep link:** `/gate-entries/{entry_id}/qc/{inspection_id}`

**Body templates:**
- SUBMITTED: `"Inspection for {material} submitted for approval."`
- QA_CHEMIST_APPROVED: `"Inspection for {material} approved by QA Chemist."`
- QAM_APPROVED: `"Inspection for {material} approved by QAM. Status: {final_status}"`

---

### 5. GRPO Posting Result

| Property     | Value                              |
|--------------|------------------------------------|
| Signal       | `post_save`                        |
| Sender       | `grpo.GRPOPosting`                 |
| Fires when   | `status` is `"POSTED"` or `"FAILED"` |
| Recipients   | All active users in the same company |
| Deep link    | `/grpo/{grpo_id}`                  |

**Status-specific behavior:**

| `status`  | Notification Type | Title                        |
|-----------|-------------------|------------------------------|
| `POSTED`  | `GRPO_POSTED`     | "GRPO Posted Successfully"   |
| `FAILED`  | `GRPO_FAILED`     | "GRPO Posting Failed"        |

**Body templates:**
- POSTED: `"GRPO for PO {po_number} posted. SAP Doc: {sap_doc_num}"`
- FAILED: `"GRPO for PO {po_number} failed: {error_message}"`

---

## Recipient Logic

All signals use the `_get_company_users()` helper:

```
_get_company_users(company, exclude_user=None)
```

1. Queries `UserCompany` where `company=<company>` and `is_active=True`
2. If `exclude_user` is provided, excludes that user from the list
3. Returns a list of `User` objects

**Rationale:**
- The user who triggers the action doesn't need a notification about their own action.
- Only users with active company membership receive notifications.

---

## Error Handling

All signal handlers are wrapped in `try/except Exception`:
- Errors are logged via `logger.error()` but do **not** crash the original save operation.
- This ensures that a notification failure never blocks the main business flow (gate entry creation, weighment recording, etc.).

---

## Adding New Signals

To add a new auto-trigger:

1. Add a new notification type in `notifications/models.py` -> `NotificationType`
2. Add a new `@receiver` function in `notifications/signals.py`
3. Run `makemigrations` if the new type changes the model choices
4. Update this documentation

**Template:**

```python
@receiver(post_save, sender="app_name.ModelName")
def notify_on_event(sender, instance, created, **kwargs):
    if not created:  # or any other condition
        return

    try:
        entry = instance.vehicle_entry  # get the gate entry for company context
        users = _get_company_users(entry.company, exclude_user=instance.created_by)
        for user in users:
            NotificationService.send_notification_to_user(
                user=user,
                title="Event Happened",
                body=f"Description of the event for {entry.entry_no}.",
                notification_type=NotificationType.NEW_TYPE,
                click_action_url=f"/some-route/{instance.id}",
                reference_type="entity_type",
                reference_id=instance.id,
                company=entry.company,
                created_by=instance.created_by,
            )
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
```
