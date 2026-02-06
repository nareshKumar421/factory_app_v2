# construction_gatein/permissions.py
"""
Permission-based access control for Construction Gate Entry module.
Uses Django's built-in permission system instead of role-based access.
"""

from rest_framework.permissions import BasePermission


# Construction Gate Entry Permissions

class CanCreateConstructionEntry(BasePermission):
    """Permission to create construction gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("construction_gatein.can_create_construction_entry")


class CanViewConstructionEntry(BasePermission):
    """Permission to view construction gate entries."""

    def has_permission(self, request, view):
        return request.user.has_perm("construction_gatein.can_view_construction_entry")


class CanEditConstructionEntry(BasePermission):
    """Permission to edit construction gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("construction_gatein.can_edit_construction_entry")


class CanDeleteConstructionEntry(BasePermission):
    """Permission to delete construction gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("construction_gatein.can_delete_construction_entry")


class CanCompleteConstructionEntry(BasePermission):
    """Permission to complete and lock construction gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("construction_gatein.can_complete_construction_entry")


# Material Category Permissions

class CanViewMaterialCategory(BasePermission):
    """Permission to view construction material categories."""

    def has_permission(self, request, view):
        return request.user.has_perm("construction_gatein.can_view_material_category")


class CanManageMaterialCategory(BasePermission):
    """Permission to manage construction material categories."""

    def has_permission(self, request, view):
        return request.user.has_perm("construction_gatein.can_manage_material_category")


# Combined permission classes for common use cases

class CanManageConstructionEntry(BasePermission):
    """Permission to create or edit construction entries."""

    def has_permission(self, request, view):
        if request.method in ["POST"]:
            return request.user.has_perm("construction_gatein.can_create_construction_entry")
        if request.method in ["PUT", "PATCH"]:
            return request.user.has_perm("construction_gatein.can_edit_construction_entry")
        if request.method in ["DELETE"]:
            return request.user.has_perm("construction_gatein.can_delete_construction_entry")
        return request.user.has_perm("construction_gatein.can_view_construction_entry")
