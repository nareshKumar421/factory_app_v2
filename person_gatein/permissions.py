# person_gatein/permissions.py
"""
Permission-based access control for Person Gate Entry module.
Uses Django's built-in permission system instead of role-based access.
"""

from rest_framework.permissions import BasePermission


# PersonType Permissions

class CanViewPersonType(BasePermission):
    """Permission to view person types."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_view_person_type")


class CanManagePersonType(BasePermission):
    """Permission to manage person types."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_manage_person_type")


# Gate Permissions

class CanViewGate(BasePermission):
    """Permission to view gates."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_view_gate")


class CanManageGate(BasePermission):
    """Permission to manage gates."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_manage_gate")


# Contractor Permissions

class CanCreateContractor(BasePermission):
    """Permission to create contractor."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_create_contractor")


class CanViewContractor(BasePermission):
    """Permission to view contractors."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_view_contractor")


class CanEditContractor(BasePermission):
    """Permission to edit contractor."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_edit_contractor")


class CanDeleteContractor(BasePermission):
    """Permission to delete contractor."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_delete_contractor")


# Visitor Permissions

class CanCreateVisitor(BasePermission):
    """Permission to create visitor."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_create_visitor")


class CanViewVisitor(BasePermission):
    """Permission to view visitors."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_view_visitor")


class CanEditVisitor(BasePermission):
    """Permission to edit visitor."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_edit_visitor")


class CanDeleteVisitor(BasePermission):
    """Permission to delete visitor."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_delete_visitor")


# Labour Permissions

class CanCreateLabour(BasePermission):
    """Permission to create labour."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_create_labour")


class CanViewLabour(BasePermission):
    """Permission to view labours."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_view_labour")


class CanEditLabour(BasePermission):
    """Permission to edit labour."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_edit_labour")


class CanDeleteLabour(BasePermission):
    """Permission to delete labour."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_delete_labour")


# Entry Log Permissions

class CanCreateEntry(BasePermission):
    """Permission to create person gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_create_entry")


class CanViewEntry(BasePermission):
    """Permission to view person gate entries."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_view_entry")


class CanEditEntry(BasePermission):
    """Permission to edit person gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_edit_entry")


class CanDeleteEntry(BasePermission):
    """Permission to delete person gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_delete_entry")


class CanCancelEntry(BasePermission):
    """Permission to cancel person gate entry."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_cancel_entry")


class CanExitEntry(BasePermission):
    """Permission to mark person gate exit."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_exit_entry")


class CanSearchEntry(BasePermission):
    """Permission to search person gate entries."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_search_entry")


class CanViewDashboard(BasePermission):
    """Permission to view person gate dashboard."""

    def has_permission(self, request, view):
        return request.user.has_perm("person_gatein.can_view_dashboard")


# Combined permission classes for ViewSets

class CanManageContractor(BasePermission):
    """Permission to manage contractors (CRUD)."""

    def has_permission(self, request, view):
        if request.method in ["POST"]:
            return request.user.has_perm("person_gatein.can_create_contractor")
        if request.method in ["PUT", "PATCH"]:
            return request.user.has_perm("person_gatein.can_edit_contractor")
        if request.method in ["DELETE"]:
            return request.user.has_perm("person_gatein.can_delete_contractor")
        return request.user.has_perm("person_gatein.can_view_contractor")


class CanManageVisitor(BasePermission):
    """Permission to manage visitors (CRUD)."""

    def has_permission(self, request, view):
        if request.method in ["POST"]:
            return request.user.has_perm("person_gatein.can_create_visitor")
        if request.method in ["PUT", "PATCH"]:
            return request.user.has_perm("person_gatein.can_edit_visitor")
        if request.method in ["DELETE"]:
            return request.user.has_perm("person_gatein.can_delete_visitor")
        return request.user.has_perm("person_gatein.can_view_visitor")


class CanManageLabour(BasePermission):
    """Permission to manage labours (CRUD)."""

    def has_permission(self, request, view):
        if request.method in ["POST"]:
            return request.user.has_perm("person_gatein.can_create_labour")
        if request.method in ["PUT", "PATCH"]:
            return request.user.has_perm("person_gatein.can_edit_labour")
        if request.method in ["DELETE"]:
            return request.user.has_perm("person_gatein.can_delete_labour")
        return request.user.has_perm("person_gatein.can_view_labour")
