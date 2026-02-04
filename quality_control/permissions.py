# quality_control/permissions.py
"""
Permission-based access control for Quality Control module.
Uses Django's built-in permission system instead of role-based access.
"""

from rest_framework.permissions import BasePermission


class CanCreateArrivalSlip(BasePermission):
    """Permission to create material arrival slip."""

    def has_permission(self, request, view):
        return request.user.has_perm("quality_control.can_create_arrival_slip")


class CanEditArrivalSlip(BasePermission):
    """Permission to edit material arrival slip."""

    def has_permission(self, request, view):
        return request.user.has_perm("quality_control.can_edit_arrival_slip")


class CanSubmitArrivalSlip(BasePermission):
    """Permission to submit arrival slip to QA."""

    def has_permission(self, request, view):
        return request.user.has_perm("quality_control.can_submit_arrival_slip")


class CanViewArrivalSlip(BasePermission):
    """Permission to view material arrival slip."""

    def has_permission(self, request, view):
        return request.user.has_perm("quality_control.can_view_arrival_slip")


class CanCreateInspection(BasePermission):
    """Permission to create raw material inspection."""

    def has_permission(self, request, view):
        return request.user.has_perm("quality_control.can_create_inspection")


class CanEditInspection(BasePermission):
    """Permission to edit raw material inspection."""

    def has_permission(self, request, view):
        return request.user.has_perm("quality_control.can_edit_inspection")


class CanSubmitInspection(BasePermission):
    """Permission to submit inspection for approval."""

    def has_permission(self, request, view):
        return request.user.has_perm("quality_control.can_submit_inspection")


class CanViewInspection(BasePermission):
    """Permission to view raw material inspection."""

    def has_permission(self, request, view):
        return request.user.has_perm("quality_control.can_view_inspection")


class CanApproveAsChemist(BasePermission):
    """Permission to approve inspection as QA Chemist."""

    def has_permission(self, request, view):
        return request.user.has_perm("quality_control.can_approve_as_chemist")


class CanApproveAsQAM(BasePermission):
    """Permission to approve inspection as QA Manager."""

    def has_permission(self, request, view):
        return request.user.has_perm("quality_control.can_approve_as_qam")


class CanRejectInspection(BasePermission):
    """Permission to reject inspection."""

    def has_permission(self, request, view):
        return request.user.has_perm("quality_control.can_reject_inspection")


class CanManageMaterialTypes(BasePermission):
    """Permission to manage material types."""

    def has_permission(self, request, view):
        return request.user.has_perm("quality_control.can_manage_material_types")


class CanManageQCParameters(BasePermission):
    """Permission to manage QC parameters."""

    def has_permission(self, request, view):
        return request.user.has_perm("quality_control.can_manage_qc_parameters")


# Combined permission classes for common use cases

class CanManageArrivalSlip(BasePermission):
    """Permission to create or edit arrival slip."""

    def has_permission(self, request, view):
        if request.method in ["POST", "PUT", "PATCH"]:
            return (
                request.user.has_perm("quality_control.can_create_arrival_slip") or
                request.user.has_perm("quality_control.can_edit_arrival_slip")
            )
        return request.user.has_perm("quality_control.can_view_arrival_slip")


class CanManageInspection(BasePermission):
    """Permission to create or edit inspection."""

    def has_permission(self, request, view):
        if request.method in ["POST", "PUT", "PATCH"]:
            return (
                request.user.has_perm("quality_control.can_create_inspection") or
                request.user.has_perm("quality_control.can_edit_inspection")
            )
        return request.user.has_perm("quality_control.can_view_inspection")
