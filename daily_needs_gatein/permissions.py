# daily_needs_gatein/permissions.py
"""
Permission-based access control for Daily Needs Gate Entry module.
Uses Django's built-in permission system instead of role-based access.
Default Django permissions (add/view/change/delete) are used for standard CRUD.
"""

from rest_framework.permissions import BasePermission


# Daily Need Gate Entry Permissions (using Django defaults for CRUD)

class CanCreateDailyNeedEntry(BasePermission):
    """Permission to create daily need gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("daily_needs_gatein.add_dailyneedgateentry")


class CanViewDailyNeedEntry(BasePermission):
    """Permission to view daily need gate entries."""

    def has_permission(self, request, view):
        return request.user.has_perm("daily_needs_gatein.view_dailyneedgateentry")


class CanEditDailyNeedEntry(BasePermission):
    """Permission to edit daily need gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("daily_needs_gatein.change_dailyneedgateentry")


class CanDeleteDailyNeedEntry(BasePermission):
    """Permission to delete daily need gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("daily_needs_gatein.delete_dailyneedgateentry")


class CanCompleteDailyNeedEntry(BasePermission):
    """Permission to complete and lock daily need gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("daily_needs_gatein.can_complete_daily_need_entry")


# Category Permissions (using Django default for view)

class CanViewCategory(BasePermission):
    """Permission to view daily need categories."""

    def has_permission(self, request, view):
        return request.user.has_perm("daily_needs_gatein.view_categorylist")


class CanManageCategory(BasePermission):
    """Permission to manage daily need categories."""

    def has_permission(self, request, view):
        return request.user.has_perm("daily_needs_gatein.can_manage_category")


# Combined permission classes for common use cases

class CanManageDailyNeedEntry(BasePermission):
    """Permission to create or edit daily need entries."""

    def has_permission(self, request, view):
        if request.method in ["POST"]:
            return request.user.has_perm("daily_needs_gatein.add_dailyneedgateentry")
        if request.method in ["PUT", "PATCH"]:
            return request.user.has_perm("daily_needs_gatein.change_dailyneedgateentry")
        if request.method in ["DELETE"]:
            return request.user.has_perm("daily_needs_gatein.delete_dailyneedgateentry")
        return request.user.has_perm("daily_needs_gatein.view_dailyneedgateentry")
