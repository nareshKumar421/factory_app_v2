# raw_material_gatein/permissions.py
"""
Permission-based access control for Raw Material Gate Entry module.
Uses Django's built-in permission system instead of role-based access.
"""

from rest_framework.permissions import BasePermission


# Raw Material Gate Entry Permissions

class CanCreateRawMaterialEntry(BasePermission):
    """Permission to create new raw material gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("raw_material_gatein.can_create_raw_material_entry")


class CanViewRawMaterialEntry(BasePermission):
    """Permission to view raw material gate entries."""

    def has_permission(self, request, view):
        return request.user.has_perm("raw_material_gatein.can_view_raw_material_entry")


class CanEditRawMaterialEntry(BasePermission):
    """Permission to edit raw material gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("raw_material_gatein.can_edit_raw_material_entry")


class CanDeleteRawMaterialEntry(BasePermission):
    """Permission to delete raw material gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("raw_material_gatein.can_delete_raw_material_entry")


class CanCompleteRawMaterialEntry(BasePermission):
    """Permission to complete and lock a raw material gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("raw_material_gatein.can_complete_raw_material_entry")


# PO Receipt Permissions

class CanReceivePO(BasePermission):
    """Permission to receive PO items against a gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("raw_material_gatein.can_receive_po")


class CanViewPOReceipt(BasePermission):
    """Permission to view PO receipts."""

    def has_permission(self, request, view):
        return request.user.has_perm("raw_material_gatein.can_view_po_receipt")


class CanEditPOReceipt(BasePermission):
    """Permission to edit PO receipts."""

    def has_permission(self, request, view):
        return request.user.has_perm("raw_material_gatein.can_edit_po_receipt")


class CanDeletePOReceipt(BasePermission):
    """Permission to delete PO receipts."""

    def has_permission(self, request, view):
        return request.user.has_perm("raw_material_gatein.can_delete_po_receipt")


# Combined permission classes for common use cases

class CanManageRawMaterialEntry(BasePermission):
    """Permission to manage raw material gate entries."""

    def has_permission(self, request, view):
        if request.method in ["POST"]:
            return request.user.has_perm("raw_material_gatein.can_create_raw_material_entry")
        if request.method in ["PUT", "PATCH"]:
            return request.user.has_perm("raw_material_gatein.can_edit_raw_material_entry")
        if request.method in ["DELETE"]:
            return request.user.has_perm("raw_material_gatein.can_delete_raw_material_entry")
        return request.user.has_perm("raw_material_gatein.can_view_raw_material_entry")


class CanManagePOReceipt(BasePermission):
    """Permission to manage PO receipts."""

    def has_permission(self, request, view):
        if request.method in ["POST"]:
            return request.user.has_perm("raw_material_gatein.can_receive_po")
        if request.method in ["PUT", "PATCH"]:
            return request.user.has_perm("raw_material_gatein.can_edit_po_receipt")
        if request.method in ["DELETE"]:
            return request.user.has_perm("raw_material_gatein.can_delete_po_receipt")
        return request.user.has_perm("raw_material_gatein.can_view_po_receipt")
