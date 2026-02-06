# maintenance_gatein/permissions.py
"""
Permission-based access control for Maintenance Gate Entry module.
Uses Django's built-in permission system instead of role-based access.
"""

from rest_framework.permissions import BasePermission


# Maintenance Gate Entry Permissions

class CanCreateMaintenanceEntry(BasePermission):
    """Permission to create maintenance gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("maintenance_gatein.can_create_maintenance_entry")


class CanViewMaintenanceEntry(BasePermission):
    """Permission to view maintenance gate entries."""

    def has_permission(self, request, view):
        return request.user.has_perm("maintenance_gatein.can_view_maintenance_entry")


class CanEditMaintenanceEntry(BasePermission):
    """Permission to edit maintenance gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("maintenance_gatein.can_edit_maintenance_entry")


class CanDeleteMaintenanceEntry(BasePermission):
    """Permission to delete maintenance gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("maintenance_gatein.can_delete_maintenance_entry")


class CanCompleteMaintenanceEntry(BasePermission):
    """Permission to complete and lock maintenance gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("maintenance_gatein.can_complete_maintenance_entry")


# Maintenance Type Permissions

class CanViewMaintenanceType(BasePermission):
    """Permission to view maintenance types."""

    def has_permission(self, request, view):
        return request.user.has_perm("maintenance_gatein.can_view_maintenance_type")


class CanManageMaintenanceType(BasePermission):
    """Permission to manage maintenance types."""

    def has_permission(self, request, view):
        return request.user.has_perm("maintenance_gatein.can_manage_maintenance_type")


# Combined permission classes for common use cases

class CanManageMaintenanceEntry(BasePermission):
    """Permission to create or edit maintenance entries."""

    def has_permission(self, request, view):
        if request.method in ["POST"]:
            return request.user.has_perm("maintenance_gatein.can_create_maintenance_entry")
        if request.method in ["PUT", "PATCH"]:
            return request.user.has_perm("maintenance_gatein.can_edit_maintenance_entry")
        if request.method in ["DELETE"]:
            return request.user.has_perm("maintenance_gatein.can_delete_maintenance_entry")
        return request.user.has_perm("maintenance_gatein.can_view_maintenance_entry")
