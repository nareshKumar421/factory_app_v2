# GRPO Models Documentation

This document describes the database models used in the GRPO app.

## Models Overview

```
VehicleEntry (driver_management)
    │
    ├── POReceipt (raw_material_gatein)
    │       │
    │       └── POItemReceipt (raw_material_gatein)
    │               │
    │               └── MaterialArrivalSlip (quality_control)
    │                       │
    │                       └── RawMaterialInspection (quality_control)
    │
    └── GRPOPosting (grpo)
            │
            └── GRPOLinePosting (grpo)
```

---

## GRPOPosting

Tracks GRPO postings to SAP for completed gate entries. One gate entry can have multiple GRPO postings (one per PO).

### Fields

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| vehicle_entry | ForeignKey | Reference to VehicleEntry |
| po_receipt | ForeignKey | Reference to POReceipt |
| sap_doc_entry | Integer | SAP DocEntry (internal ID) |
| sap_doc_num | Integer | SAP DocNum (visible document number) |
| sap_doc_total | Decimal | Total document value |
| status | CharField | Posting status (PENDING, POSTED, FAILED, PARTIALLY_POSTED) |
| error_message | TextField | Error message if posting failed |
| posted_at | DateTime | When GRPO was posted |
| posted_by | ForeignKey | User who posted the GRPO |
| created_at | DateTime | Record creation time |
| updated_at | DateTime | Record last update time |

### Constraints

- `unique_together`: (vehicle_entry, po_receipt) - One GRPO per PO per gate entry

### Status Values

```python
class GRPOStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    POSTED = "POSTED", "Posted to SAP"
    FAILED = "FAILED", "Failed"
    PARTIALLY_POSTED = "PARTIALLY_POSTED", "Partially Posted"
```

### Example

```python
from grpo.models import GRPOPosting, GRPOStatus

# Create a GRPO posting record
grpo = GRPOPosting.objects.create(
    vehicle_entry=vehicle_entry,
    po_receipt=po_receipt,
    status=GRPOStatus.PENDING,
    posted_by=user
)

# After successful SAP posting
grpo.sap_doc_entry = 12345
grpo.sap_doc_num = 1001
grpo.sap_doc_total = Decimal("47500.00")
grpo.status = GRPOStatus.POSTED
grpo.posted_at = timezone.now()
grpo.save()
```

---

## GRPOLinePosting

Tracks individual line items posted in a GRPO. Links to POItemReceipt for traceability.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| grpo_posting | ForeignKey | Reference to GRPOPosting |
| po_item_receipt | ForeignKey | Reference to POItemReceipt |
| quantity_posted | Decimal | Quantity posted to SAP |
| base_entry | Integer | PO DocEntry in SAP (for PO linking) |
| base_line | Integer | PO Line Number in SAP (for PO linking) |

### Relationships

- `grpo_posting`: Many-to-one relationship with GRPOPosting (accessed via `grpo_posting.lines`)
- `po_item_receipt`: Many-to-one relationship with POItemReceipt (accessed via `po_item_receipt.grpo_lines`)

### Example

```python
from grpo.models import GRPOLinePosting

# Create line posting after successful GRPO
line = GRPOLinePosting.objects.create(
    grpo_posting=grpo_posting,
    po_item_receipt=po_item,
    quantity_posted=po_item.accepted_qty
)
```

---

## Related Models (External)

### VehicleEntry (driver_management)

Gate entry record for vehicle arrival.

| Key Fields | Description |
|------------|-------------|
| entry_no | Gate entry number (e.g., "VE-2024-001") |
| status | Entry status (COMPLETED, QC_COMPLETED, etc.) |
| entry_type | Type of entry (RAW_MATERIAL, MAINTENANCE, etc.) |
| company | Associated company |

### POReceipt (raw_material_gatein)

Purchase order receipt linked to a gate entry.

| Key Fields | Description |
|------------|-------------|
| po_number | PO number from SAP |
| supplier_code | Supplier/vendor code |
| supplier_name | Supplier name |
| invoice_no | Invoice number |

### POItemReceipt (raw_material_gatein)

Individual PO line items received.

| Key Fields | Description |
|------------|-------------|
| po_item_code | Item code |
| item_name | Item description |
| ordered_qty | Original ordered quantity |
| received_qty | Quantity received at gate |
| accepted_qty | QC accepted quantity (posted to GRPO) |
| rejected_qty | QC rejected quantity |

---

## Database Schema

```sql
CREATE TABLE grpo_grpoposting (
    id BIGSERIAL PRIMARY KEY,
    vehicle_entry_id BIGINT NOT NULL REFERENCES driver_management_vehicleentry(id),
    po_receipt_id BIGINT NOT NULL REFERENCES raw_material_gatein_poreceipt(id),
    sap_doc_entry INTEGER,
    sap_doc_num INTEGER,
    sap_doc_total DECIMAL(18,2),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    error_message TEXT,
    posted_at TIMESTAMP WITH TIME ZONE,
    posted_by_id BIGINT REFERENCES accounts_user(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE (vehicle_entry_id, po_receipt_id)
);

CREATE TABLE grpo_grpolineposting (
    id BIGSERIAL PRIMARY KEY,
    grpo_posting_id BIGINT NOT NULL REFERENCES grpo_grpoposting(id),
    po_item_receipt_id BIGINT NOT NULL REFERENCES raw_material_gatein_poitemreceipt(id),
    quantity_posted DECIMAL(12,3) NOT NULL,
    base_entry INTEGER,
    base_line INTEGER
);

CREATE INDEX grpo_grpoposting_status_idx ON grpo_grpoposting(status);
CREATE INDEX grpo_grpoposting_posted_at_idx ON grpo_grpoposting(posted_at);
```

---

## Querying Examples

### Get all pending GRPO postings
```python
GRPOPosting.objects.filter(status=GRPOStatus.PENDING)
```

### Get GRPO history for a vehicle entry
```python
GRPOPosting.objects.filter(
    vehicle_entry_id=123
).select_related('po_receipt').prefetch_related('lines')
```

### Get total posted quantity for an item
```python
from django.db.models import Sum

total = GRPOLinePosting.objects.filter(
    po_item_receipt_id=456,
    grpo_posting__status=GRPOStatus.POSTED
).aggregate(total=Sum('quantity_posted'))['total']
```
