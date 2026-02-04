from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from company.permissions import HasCompanyContext
from driver_management.models import VehicleEntry
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError

class RawMaterialGateEntryFullView(APIView):
    """
    Get complete raw material gate entry data (read-only)
    """
    permission_classes = [IsAuthenticated, HasCompanyContext]
    def get(self, request, gate_entry_id):

        try:
            entry = (
                VehicleEntry.objects
                .select_related(
                    "vehicle",
                    "driver",
                    "security_check",
                    "weighment"
                )
                .prefetch_related(
                    "po_receipts__items__arrival_slip__inspection"
                )
                .get(id=gate_entry_id)
            )
        except VehicleEntry.DoesNotExist:
            raise NotFound("Gate entry not found")

        response = {
            "gate_entry": {
                "id": entry.id,
                "entry_no": entry.entry_no,
                "status": entry.status,
                "is_locked": entry.is_locked,
                "created_at": entry.created_at,
            },

            "vehicle": {
                "vehicle_number": entry.vehicle.vehicle_number,
                "vehicle_type": entry.vehicle.vehicle_type,
                "capacity_ton": entry.vehicle.capacity_ton,
            },

            "driver": {
                "name": entry.driver.name,
                "mobile_no": entry.driver.mobile_no,
                "license_no": entry.driver.license_no,
            },

            "security_check": None,
            "weighment": None,
            "po_receipts": [],
        }

        # -------------------------
        # SECURITY CHECK
        # -------------------------
        if hasattr(entry, "security_check") and entry.security_check:
            sc = entry.security_check
            response["security_check"] = {
                "vehicle_condition_ok": sc.vehicle_condition_ok,
                "tyre_condition_ok": sc.tyre_condition_ok,
                "fire_extinguisher_available": sc.fire_extinguisher_available,
                "alcohol_test_done": sc.alcohol_test_done,
                "alcohol_test_passed": sc.alcohol_test_passed,
                "is_submitted": sc.is_submitted,
                "remarks": sc.remarks,
                "inspected_by": sc.inspected_by_name,
            }

        # -------------------------
        # WEIGHMENT
        # -------------------------
        if hasattr(entry, "weighment") and entry.weighment:
            w = entry.weighment
            response["weighment"] = {
                "gross_weight": w.gross_weight,
                "tare_weight": w.tare_weight,
                "net_weight": w.net_weight,
                "weighbridge_slip_no": w.weighbridge_slip_no,
            }

        # -------------------------
        # PO RECEIPTS + ITEMS + QC
        # -------------------------
        for po in entry.po_receipts.all():
            po_data = {
                "po_number": po.po_number,
                "supplier_code": po.supplier_code,
                "supplier_name": po.supplier_name,
                "created_by": (
                    po.created_by.email
                    if po.created_by else None
                ),
                "items": []
            }

            for item in po.items.all():
                arrival_slip = getattr(item, "arrival_slip", None)
                inspection = getattr(arrival_slip, "inspection", None) if arrival_slip else None

                item_data = {
                    "item_code": item.po_item_code,
                    "item_name": item.item_name,
                    "ordered_qty": float(item.ordered_qty),
                    "received_qty": float(item.received_qty),
                    "short_qty": float(item.short_qty),
                    "uom": item.uom,
                    "arrival_slip": None,
                    "inspection": None
                }

                if arrival_slip:
                    item_data["arrival_slip"] = {
                        "id": arrival_slip.id,
                        "status": arrival_slip.status,
                        "is_submitted": arrival_slip.is_submitted,
                    }

                if inspection:
                    item_data["inspection"] = {
                        "id": inspection.id,
                        "report_no": inspection.report_no,
                        "workflow_status": inspection.workflow_status,
                        "final_status": inspection.final_status,
                        "remarks": inspection.remarks,
                    }

                po_data["items"].append(item_data)

            response["po_receipts"].append(po_data)

        return Response(response)
    

class DailyNeedGateEntryFullView(APIView):
    """
    Get complete Daily Need / Canteen gate entry data
    (Human readable, no serializers)
    """

    def get(self, request, gate_entry_id):

        try:
            entry = (
                VehicleEntry.objects
                .select_related(
                    "vehicle",
                    "driver",
                    "security_check",
                    "daily_need_entry"
                )
                .get(id=gate_entry_id)
            )
        except VehicleEntry.DoesNotExist:
            raise NotFound("Gate entry not found")

        # ✅ ensure correct type
        if entry.entry_type != "DAILY_NEED":
            raise ValidationError("Not a daily need gate entry")

        daily = getattr(entry, "daily_need_entry", None)
        security = getattr(entry, "security_check", None)

        response = {
            # -----------------------
            # Gate Info
            # -----------------------
            "gate_entry": {
                "id": entry.id,
                "entry_no": entry.entry_no,
                "status": entry.status,
                "is_locked": entry.is_locked,
                "created_at": entry.created_at,
                "entry_type": entry.entry_type,
            },

            # -----------------------
            # Vehicle
            # -----------------------
            "vehicle": {
                "vehicle_number": entry.vehicle.vehicle_number,
                "vehicle_type": entry.vehicle.vehicle_type,
                "capacity_ton": entry.vehicle.capacity_ton,
            },

            # -----------------------
            # Driver
            # -----------------------
            "driver": {
                "name": entry.driver.name,
                "mobile_no": entry.driver.mobile_no,
                "license_no": entry.driver.license_no,
            },

            # -----------------------
            # Security
            # -----------------------
            "security_check": None,

            # -----------------------
            # Daily Need Details
            # -----------------------
            "daily_need_details": None,
        }

        # =========================
        # SECURITY SECTION
        # =========================
        if security:
            response["security_check"] = {
                "vehicle_condition_ok": security.vehicle_condition_ok,
                "tyre_condition_ok": security.tyre_condition_ok,
                "alcohol_test_passed": security.alcohol_test_passed,
                "is_submitted": security.is_submitted,
                "remarks": security.remarks,
                "inspected_by": (
                    security.inspected_by_name
                ),
            }

        # =========================
        # DAILY NEED SECTION
        # =========================
        if daily:
            response["daily_need_details"] = {
                "category": daily.item_category.category_name,
                "supplier_name": daily.supplier_name,
                "material_name": daily.material_name,
                "quantity": float(daily.quantity),
                "unit": daily.unit,
                "receiving_department": daily.receiving_department.name,

                "bill_number": daily.bill_number,
                "delivery_challan_number": daily.delivery_challan_number,

                "canteen_supervisor": daily.canteen_supervisor,
                "vehicle_or_person_name": daily.vehicle_or_person_name,
                "contact_number": daily.contact_number,

                "remarks": daily.remarks,

                "created_by": (
                    daily.created_by.email
                    if daily.created_by else None
                ),
                "created_at": daily.created_at,
            }

        return Response(response)


class MaintenanceGateEntryFullView(APIView):
    """
    Get complete Maintenance & Repair Material gate entry data
    (Human readable, no serializers)
    """

    def get(self, request, gate_entry_id):

        try:
            entry = (
                VehicleEntry.objects
                .select_related(
                    "vehicle",
                    "driver",
                    "security_check",
                    "maintenance_entry",
                    "maintenance_entry__maintenance_type",
                    "maintenance_entry__receiving_department",
                    "maintenance_entry__created_by",
                )
                .get(id=gate_entry_id)
            )
        except VehicleEntry.DoesNotExist:
            raise NotFound("Gate entry not found")

        # Ensure correct type
        if entry.entry_type != "MAINTENANCE":
            raise ValidationError("Not a maintenance gate entry")

        maintenance = getattr(entry, "maintenance_entry", None)
        security = getattr(entry, "security_check", None)

        response = {
            # -----------------------
            # Gate Info
            # -----------------------
            "gate_entry": {
                "id": entry.id,
                "entry_no": entry.entry_no,
                "status": entry.status,
                "is_locked": entry.is_locked,
                "created_at": entry.created_at,
                "entry_type": entry.entry_type,
            },

            # -----------------------
            # Vehicle
            # -----------------------
            "vehicle": {
                "vehicle_number": entry.vehicle.vehicle_number,
                "vehicle_type": entry.vehicle.vehicle_type,
                "capacity_ton": entry.vehicle.capacity_ton,
            },

            # -----------------------
            # Driver
            # -----------------------
            "driver": {
                "name": entry.driver.name,
                "mobile_no": entry.driver.mobile_no,
                "license_no": entry.driver.license_no,
            },

            # -----------------------
            # Security
            # -----------------------
            "security_check": None,

            # -----------------------
            # Maintenance Details
            # -----------------------
            "maintenance_details": None,
        }

        # =========================
        # SECURITY SECTION
        # =========================
        if security:
            response["security_check"] = {
                "vehicle_condition_ok": security.vehicle_condition_ok,
                "tyre_condition_ok": security.tyre_condition_ok,
                "alcohol_test_passed": security.alcohol_test_passed,
                "is_submitted": security.is_submitted,
                "remarks": security.remarks,
                "inspected_by": security.inspected_by_name,
            }

        # =========================
        # MAINTENANCE SECTION
        # =========================
        if maintenance:
            response["maintenance_details"] = {
                "work_order_number": maintenance.work_order_number,
                "maintenance_type": (
                    maintenance.maintenance_type.type_name
                    if maintenance.maintenance_type else None
                ),
                "supplier_name": maintenance.supplier_name,
                "material_description": maintenance.material_description,
                "part_number": maintenance.part_number,
                "quantity": float(maintenance.quantity),
                "unit": maintenance.unit,
                "invoice_number": maintenance.invoice_number,
                "equipment_id": maintenance.equipment_id,
                "receiving_department": (
                    maintenance.receiving_department.name
                    if maintenance.receiving_department else None
                ),
                "urgency_level": maintenance.urgency_level,
                "inward_time": maintenance.inward_time,
                "remarks": maintenance.remarks,
                "created_by": (
                    maintenance.created_by.email
                    if maintenance.created_by else None
                ),
                "created_at": maintenance.created_at,
            }

        return Response(response)


class ConstructionGateEntryFullView(APIView):
    """
    Get complete Construction / Civil Work Material gate entry data
    (Human readable, no serializers)
    """

    def get(self, request, gate_entry_id):

        try:
            entry = (
                VehicleEntry.objects
                .select_related(
                    "vehicle",
                    "driver",
                    "security_check",
                    "construction_entry",
                    "construction_entry__material_category",
                    "construction_entry__created_by",
                )
                .get(id=gate_entry_id)
            )
        except VehicleEntry.DoesNotExist:
            raise NotFound("Gate entry not found")

        # Ensure correct type
        if entry.entry_type != "CONSTRUCTION":
            raise ValidationError("Not a construction gate entry")

        construction = getattr(entry, "construction_entry", None)
        security = getattr(entry, "security_check", None)

        response = {
            # -----------------------
            # Gate Info
            # -----------------------
            "gate_entry": {
                "id": entry.id,
                "entry_no": entry.entry_no,
                "status": entry.status,
                "is_locked": entry.is_locked,
                "created_at": entry.created_at,
                "entry_type": entry.entry_type,
            },

            # -----------------------
            # Vehicle
            # -----------------------
            "vehicle": {
                "vehicle_number": entry.vehicle.vehicle_number,
                "vehicle_type": entry.vehicle.vehicle_type,
                "capacity_ton": entry.vehicle.capacity_ton,
            },

            # -----------------------
            # Driver
            # -----------------------
            "driver": {
                "name": entry.driver.name,
                "mobile_no": entry.driver.mobile_no,
                "license_no": entry.driver.license_no,
            },

            # -----------------------
            # Security
            # -----------------------
            "security_check": None,

            # -----------------------
            # Construction Details
            # -----------------------
            "construction_details": None,
        }

        # =========================
        # SECURITY SECTION
        # =========================
        if security:
            response["security_check"] = {
                "vehicle_condition_ok": security.vehicle_condition_ok,
                "tyre_condition_ok": security.tyre_condition_ok,
                "alcohol_test_passed": security.alcohol_test_passed,
                "is_submitted": security.is_submitted,
                "remarks": security.remarks,
                "inspected_by": security.inspected_by_name,
            }

        # =========================
        # CONSTRUCTION SECTION
        # =========================
        if construction:
            response["construction_details"] = {
                "work_order_number": construction.work_order_number,
                "project_name": construction.project_name,
                "material_category": (
                    construction.material_category.category_name
                    if construction.material_category else None
                ),
                "contractor_name": construction.contractor_name,
                "contractor_contact": construction.contractor_contact,
                "material_description": construction.material_description,
                "quantity": float(construction.quantity),
                "unit": construction.unit,
                "challan_number": construction.challan_number,
                "invoice_number": construction.invoice_number,
                "site_engineer": construction.site_engineer,
                "security_approval": construction.security_approval,
                "inward_time": construction.inward_time,
                "remarks": construction.remarks,
                "created_by": (
                    construction.created_by.email
                    if construction.created_by else None
                ),
                "created_at": construction.created_at,
            }

        return Response(response)
