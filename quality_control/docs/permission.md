# Quality Control - Permission Documentation

## Authentication

All API endpoints require:
- `Authorization: Bearer <access_token>`
- `Company-Code: <company_code>`

---

## API Endpoints & Required Permissions

### Material Type APIs

| # | API Endpoint | Method | View Class | Permission Class | Permission Codename |
|---|-------------|--------|------------|-----------------|---------------------|
| 1 | `/material-types/` | GET | `MaterialTypeListCreateAPI` | `CanManageMaterialTypes` | `quality_control.can_manage_material_types` |
| 2 | `/material-types/` | POST | `MaterialTypeListCreateAPI` | `CanManageMaterialTypes` | `quality_control.can_manage_material_types` |
| 3 | `/material-types/{id}/` | GET | `MaterialTypeDetailAPI` | `CanManageMaterialTypes` | `quality_control.can_manage_material_types` |
| 4 | `/material-types/{id}/` | PUT | `MaterialTypeDetailAPI` | `CanManageMaterialTypes` | `quality_control.can_manage_material_types` |
| 5 | `/material-types/{id}/` | DELETE | `MaterialTypeDetailAPI` | `CanManageMaterialTypes` | `quality_control.can_manage_material_types` |

### QC Parameter APIs

| # | API Endpoint | Method | View Class | Permission Class | Permission Codename |
|---|-------------|--------|------------|-----------------|---------------------|
| 6 | `/material-types/{id}/parameters/` | GET | `QCParameterListCreateAPI` | `CanManageQCParameters` | `quality_control.can_manage_qc_parameters` |
| 7 | `/material-types/{id}/parameters/` | POST | `QCParameterListCreateAPI` | `CanManageQCParameters` | `quality_control.can_manage_qc_parameters` |
| 8 | `/parameters/{id}/` | GET | `QCParameterDetailAPI` | `CanManageQCParameters` | `quality_control.can_manage_qc_parameters` |
| 9 | `/parameters/{id}/` | PUT | `QCParameterDetailAPI` | `CanManageQCParameters` | `quality_control.can_manage_qc_parameters` |
| 10 | `/parameters/{id}/` | DELETE | `QCParameterDetailAPI` | `CanManageQCParameters` | `quality_control.can_manage_qc_parameters` |

### Material Arrival Slip APIs

| # | API Endpoint | Method | View Class | Permission Class | Permission Codename |
|---|-------------|--------|------------|-----------------|---------------------|
| 11 | `/arrival-slips/` | GET | `ArrivalSlipListAPI` | `CanViewArrivalSlip` | `quality_control.view_materialarrivalslip` |
| 12 | `/po-items/{id}/arrival-slip/` | GET | `ArrivalSlipCreateUpdateAPI` | `CanManageArrivalSlip` | `quality_control.view_materialarrivalslip` |
| 13 | `/po-items/{id}/arrival-slip/` | POST | `ArrivalSlipCreateUpdateAPI` | `CanManageArrivalSlip` | `quality_control.add_materialarrivalslip` or `quality_control.change_materialarrivalslip` |
| 14 | `/arrival-slips/{id}/` | GET | `ArrivalSlipDetailAPI` | `CanViewArrivalSlip` | `quality_control.view_materialarrivalslip` |
| 15 | `/arrival-slips/{id}/submit/` | POST | `ArrivalSlipSubmitAPI` | `CanSubmitArrivalSlip` | `quality_control.can_submit_arrival_slip` |

### Raw Material Inspection APIs

| # | API Endpoint | Method | View Class | Permission Class | Permission Codename |
|---|-------------|--------|------------|-----------------|---------------------|
| 16 | `/inspections/pending/` | GET | `InspectionPendingListAPI` | `CanViewInspection` | `quality_control.view_rawmaterialinspection` |
| 17 | `/arrival-slips/{id}/inspection/` | GET | `InspectionCreateUpdateAPI` | `CanManageInspection` | `quality_control.view_rawmaterialinspection` |
| 18 | `/arrival-slips/{id}/inspection/` | POST | `InspectionCreateUpdateAPI` | `CanManageInspection` | `quality_control.add_rawmaterialinspection` or `quality_control.change_rawmaterialinspection` |
| 19 | `/inspections/{id}/` | GET | `InspectionDetailAPI` | `CanViewInspection` | `quality_control.view_rawmaterialinspection` |
| 20 | `/inspections/{id}/parameters/` | GET | `InspectionParameterResultsAPI` | `CanManageInspection` | `quality_control.view_rawmaterialinspection` |
| 21 | `/inspections/{id}/parameters/` | POST | `InspectionParameterResultsAPI` | `CanManageInspection` | `quality_control.add_rawmaterialinspection` or `quality_control.change_rawmaterialinspection` |
| 22 | `/inspections/{id}/submit/` | POST | `InspectionSubmitAPI` | `CanSubmitInspection` | `quality_control.can_submit_inspection` |

### Approval APIs

| # | API Endpoint | Method | View Class | Permission Class | Permission Codename |
|---|-------------|--------|------------|-----------------|---------------------|
| 23 | `/inspections/{id}/approve/chemist/` | POST | `InspectionApproveChemistAPI` | `CanApproveAsChemist` | `quality_control.can_approve_as_chemist` |
| 24 | `/inspections/{id}/approve/qam/` | POST | `InspectionApproveQAMAPI` | `CanApproveAsQAM` | `quality_control.can_approve_as_qam` |
| 25 | `/inspections/{id}/reject/` | POST | `InspectionRejectAPI` | `CanRejectInspection` | `quality_control.can_reject_inspection` |

---

## All Permission Codenames

### Django Default Permissions (auto-generated)

| Permission Codename | Description |
|---------------------|-------------|
| `quality_control.add_materialarrivalslip` | Can add material arrival slip |
| `quality_control.view_materialarrivalslip` | Can view material arrival slip |
| `quality_control.change_materialarrivalslip` | Can change material arrival slip |
| `quality_control.delete_materialarrivalslip` | Can delete material arrival slip |
| `quality_control.add_rawmaterialinspection` | Can add raw material inspection |
| `quality_control.view_rawmaterialinspection` | Can view raw material inspection |
| `quality_control.change_rawmaterialinspection` | Can change raw material inspection |
| `quality_control.delete_rawmaterialinspection` | Can delete raw material inspection |
| `quality_control.add_materialtype` | Can add material type |
| `quality_control.view_materialtype` | Can view material type |
| `quality_control.change_materialtype` | Can change material type |
| `quality_control.delete_materialtype` | Can delete material type |
| `quality_control.add_qcparametermaster` | Can add QC parameter master |
| `quality_control.view_qcparametermaster` | Can view QC parameter master |
| `quality_control.change_qcparametermaster` | Can change QC parameter master |
| `quality_control.delete_qcparametermaster` | Can delete QC parameter master |
| `quality_control.add_inspectionparameterresult` | Can add inspection parameter result |
| `quality_control.view_inspectionparameterresult` | Can view inspection parameter result |
| `quality_control.change_inspectionparameterresult` | Can change inspection parameter result |
| `quality_control.delete_inspectionparameterresult` | Can delete inspection parameter result |

### Custom Permissions (defined in model Meta)

| Permission Codename | Description | Model |
|---------------------|-------------|-------|
| `quality_control.can_submit_arrival_slip` | Can submit arrival slip to QA | `MaterialArrivalSlip` |
| `quality_control.can_submit_inspection` | Can submit inspection for approval | `RawMaterialInspection` |
| `quality_control.can_approve_as_chemist` | Can approve inspection as QA Chemist | `RawMaterialInspection` |
| `quality_control.can_approve_as_qam` | Can approve inspection as QA Manager | `RawMaterialInspection` |
| `quality_control.can_reject_inspection` | Can reject inspection | `RawMaterialInspection` |
| `quality_control.can_manage_material_types` | Can manage material types | `MaterialType` |
| `quality_control.can_manage_qc_parameters` | Can manage QC parameters | `MaterialType` |

---

## Permission Classes (in permissions.py)

| Class Name | Type | Checks Permission |
|------------|------|-------------------|
| `CanCreateArrivalSlip` | Single | `quality_control.add_materialarrivalslip` |
| `CanEditArrivalSlip` | Single | `quality_control.change_materialarrivalslip` |
| `CanViewArrivalSlip` | Single | `quality_control.view_materialarrivalslip` |
| `CanSubmitArrivalSlip` | Single | `quality_control.can_submit_arrival_slip` |
| `CanCreateInspection` | Single | `quality_control.add_rawmaterialinspection` |
| `CanEditInspection` | Single | `quality_control.change_rawmaterialinspection` |
| `CanViewInspection` | Single | `quality_control.view_rawmaterialinspection` |
| `CanSubmitInspection` | Single | `quality_control.can_submit_inspection` |
| `CanApproveAsChemist` | Single | `quality_control.can_approve_as_chemist` |
| `CanApproveAsQAM` | Single | `quality_control.can_approve_as_qam` |
| `CanRejectInspection` | Single | `quality_control.can_reject_inspection` |
| `CanManageMaterialTypes` | Single | `quality_control.can_manage_material_types` |
| `CanManageQCParameters` | Single | `quality_control.can_manage_qc_parameters` |
| `CanManageArrivalSlip` | Combined | POST/PUT/PATCH: `add_materialarrivalslip` or `change_materialarrivalslip`, GET: `view_materialarrivalslip` |
| `CanManageInspection` | Combined | POST/PUT/PATCH: `add_rawmaterialinspection` or `change_rawmaterialinspection`, GET: `view_rawmaterialinspection` |

---

## Groups

### qc_store
Store/security personnel who handle arrival slips.

| Permission Codename |
|---------------------|
| `quality_control.add_materialarrivalslip` |
| `quality_control.view_materialarrivalslip` |
| `quality_control.change_materialarrivalslip` |
| `quality_control.can_submit_arrival_slip` |
| `quality_control.view_rawmaterialinspection` |

### qc_chemist
QA Chemists who perform inspections and approve.

| Permission Codename |
|---------------------|
| `quality_control.view_materialarrivalslip` |
| `quality_control.add_rawmaterialinspection` |
| `quality_control.view_rawmaterialinspection` |
| `quality_control.change_rawmaterialinspection` |
| `quality_control.can_submit_inspection` |
| `quality_control.can_approve_as_chemist` |

### qc_manager
QA Managers with full access to all QC operations.

All permissions from the `quality_control` app.
