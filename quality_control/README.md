# Quality Control Module

## Overview

The **Quality Control Module** handles the quality control workflow for raw material inspection at the factory gates. It supports dynamic QC parameters per material type and a multi-level approval workflow.

---

## Data Flow

```
POItemReceipt
      | (OneToOne)
MaterialArrivalSlip (Security Guard fills)
      | (OneToOne)
RawMaterialInspection (QA fills)
      | (ForeignKey)
InspectionParameterResult (Dynamic parameters)
```

---

## Models

### MaterialType
Master data for material types. Each material type can have different QC parameters.

### QCParameterMaster
Defines QC parameters for each material type (e.g., Weight, Colour, pH).

### MaterialArrivalSlip
Created by Security Guard for each PO item that arrives. Contains arrival information, transport details, and document references.

### RawMaterialInspection
Created by QA/Lab personnel for each arrival slip. Contains inspection results and approval chain.

### InspectionParameterResult
Stores actual test results for each QC parameter.

---

## Workflow Status States

### Arrival Slip Status
| Status | Description |
|--------|-------------|
| `DRAFT` | Initial state, can be edited |
| `SUBMITTED` | Submitted to QA |
| `REJECTED` | Rejected by QA, sent back to security |

### Inspection Workflow Status
| Status | Description |
|--------|-------------|
| `DRAFT` | Initial state, can be edited |
| `SUBMITTED` | Submitted for QA Chemist approval |
| `QA_CHEMIST_APPROVED` | Approved by QA Chemist, awaiting QAM |
| `QAM_APPROVED` | Approved by QA Manager |
| `COMPLETED` | Workflow completed |

### Inspection Final Status
| Status | Description |
|--------|-------------|
| `PENDING` | Awaiting inspection result |
| `ACCEPTED` | Material accepted |
| `REJECTED` | Material rejected |
| `HOLD` | Material on hold |

---

## API Documentation

See [api_doc.md](./api_doc.md) for complete API documentation.

---

## Module Structure

```
quality_control/
├── __init__.py
├── apps.py
├── models/
│   ├── __init__.py
│   ├── material_type.py
│   ├── qc_parameter_master.py
│   ├── material_arrival_slip.py
│   ├── raw_material_inspection.py
│   └── inspection_parameter_result.py
├── enums.py
├── serializers.py
├── views.py
├── urls.py
├── permissions.py
├── admin.py
├── api_doc.md
└── migrations/
```

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `raw_material_gatein` | Parent POItemReceipt |
| `driver_management` | VehicleEntry status updates |
| `company` | Company context for multi-tenancy |
