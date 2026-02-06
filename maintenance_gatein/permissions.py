# maintenance_gatein/permissions.py
"""
Permission-based access control for Maintenance Gate Entry module.
Uses Django's built-in permission system instead of role-based access.
Default Django permissions (add/view/change/delete) are used for standard CRUD.
"""

from rest_framework.permissions import BasePermission


# Maintenance Gate Entry Permissions (using Django defaults for CRUD)

class CanCreateMaintenanceEntry(BasePermission):
    """Permission to create maintenance gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("maintenance_gatein.add_maintenancegateentry")


class CanViewMaintenanceEntry(BasePermission):
    """Permission to view maintenance gate entries."""

    def has_permission(self, request, view):
        return request.user.has_perm("maintenance_gatein.view_maintenancegateentry")


class CanEditMaintenanceEntry(BasePermission):
    """Permission to edit maintenance gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("maintenance_gatein.change_maintenancegateentry")


class CanDeleteMaintenanceEntry(BasePermission):
    """Permission to delete maintenance gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("maintenance_gatein.delete_maintenancegateentry")


class CanCompleteMaintenanceEntry(BasePermission):
    """Permission to complete and lock maintenance gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("maintenance_gatein.can_complete_maintenance_entry")


# Maintenance Type Permissions (using Django default for view)

class CanViewMaintenanceType(BasePermission):
    """Permission to view maintenance types."""

    def has_permission(self, request, view):
        return request.user.has_perm("maintenance_gatein.view_maintenancetype")


class CanManageMaintenanceType(BasePermission):
    """Permission to manage maintenance types."""

    def has_permission(self, request, view):
        return request.user.has_perm("maintenance_gatein.can_manage_maintenance_type")


# Combined permission classes for common use cases

class CanManageMaintenanceEntry(BasePermission):
    """Permission to create or edit maintenance entries."""

    def has_permission(self, request, view):
        if request.method in ["POST"]:
            return request.user.has_perm("maintenance_gatein.add_maintenancegateentry")
        if request.method in ["PUT", "PATCH"]:
            return request.user.has_perm("maintenance_gatein.change_maintenancegateentry")
        if request.method in ["DELETE"]:
            return request.user.has_perm("maintenance_gatein.delete_maintenancegateentry")
        return request.user.has_perm("maintenance_gatein.view_maintenancegateentry")
