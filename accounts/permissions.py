# accounts/permissions.py
"""
Permission-based access control for Accounts module.
Uses Django's built-in permission system instead of role-based access.
"""

from rest_framework.permissions import BasePermission


class CanCreateUser(BasePermission):
    """Permission to create new users."""

    def has_permission(self, request, view):
        return request.user.has_perm("accounts.can_create_user")


class CanEditUser(BasePermission):
    """Permission to edit user details."""

    def has_permission(self, request, view):
        return request.user.has_perm("accounts.can_edit_user")


class CanViewUser(BasePermission):
    """Permission to view user details."""

    def has_permission(self, request, view):
        return request.user.has_perm("accounts.can_view_user")


class CanDeleteUser(BasePermission):
    """Permission to delete users."""

    def has_permission(self, request, view):
        return request.user.has_perm("accounts.can_delete_user")


class CanManageUserPermissions(BasePermission):
    """Permission to manage user permissions and group assignments."""

    def has_permission(self, request, view):
        return request.user.has_perm("accounts.can_manage_user_permissions")


class CanViewDepartment(BasePermission):
    """Permission to view departments."""

    def has_permission(self, request, view):
        return request.user.has_perm("accounts.can_view_department")


class CanManageDepartment(BasePermission):
    """Permission to create, edit, and delete departments."""

    def has_permission(self, request, view):
        return request.user.has_perm("accounts.can_manage_department")


# Combined permission classes for common use cases

class CanManageUser(BasePermission):
    """Permission to create or edit users."""

    def has_permission(self, request, view):
        if request.method in ["POST"]:
            return request.user.has_perm("accounts.can_create_user")
        if request.method in ["PUT", "PATCH"]:
            return request.user.has_perm("accounts.can_edit_user")
        if request.method in ["DELETE"]:
            return request.user.has_perm("accounts.can_delete_user")
        return request.user.has_perm("accounts.can_view_user")
