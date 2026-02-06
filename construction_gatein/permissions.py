# construction_gatein/permissions.py
"""
Permission-based access control for Construction Gate Entry module.
Uses Django's built-in permission system instead of role-based access.
Default Django permissions (add/view/change/delete) are used for standard CRUD.
"""

from rest_framework.permissions import BasePermission


# Construction Gate Entry Permissions (using Django defaults for CRUD)

class CanCreateConstructionEntry(BasePermission):
    """Permission to create construction gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("construction_gatein.add_constructiongateentry")


class CanViewConstructionEntry(BasePermission):
    """Permission to view construction gate entries."""

    def has_permission(self, request, view):
        return request.user.has_perm("construction_gatein.view_constructiongateentry")


class CanEditConstructionEntry(BasePermission):
    """Permission to edit construction gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("construction_gatein.change_constructiongateentry")


class CanDeleteConstructionEntry(BasePermission):
    """Permission to delete construction gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("construction_gatein.delete_constructiongateentry")


class CanCompleteConstructionEntry(BasePermission):
    """Permission to complete and lock construction gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("construction_gatein.can_complete_construction_entry")


# Material Category Permissions (using Django default for view)

class CanViewMaterialCategory(BasePermission):
    """Permission to view construction material categories."""

    def has_permission(self, request, view):
        return request.user.has_perm("construction_gatein.view_constructionmaterialcategory")


class CanManageMaterialCategory(BasePermission):
    """Permission to manage construction material categories."""

    def has_permission(self, request, view):
        return request.user.has_perm("construction_gatein.can_manage_material_category")


# Combined permission classes for common use cases

class CanManageConstructionEntry(BasePermission):
    """Permission to create or edit construction entries."""

    def has_permission(self, request, view):
        if request.method in ["POST"]:
            return request.user.has_perm("construction_gatein.add_constructiongateentry")
        if request.method in ["PUT", "PATCH"]:
            return request.user.has_perm("construction_gatein.change_constructiongateentry")
        if request.method in ["DELETE"]:
            return request.user.has_perm("construction_gatein.delete_constructiongateentry")
        return request.user.has_perm("construction_gatein.view_constructiongateentry")
