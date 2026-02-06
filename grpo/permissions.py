# grpo/permissions.py
"""
Permission-based access control for GRPO module.
Uses Django's built-in permission system instead of role-based access.
"""

from rest_framework.permissions import BasePermission


# GRPO Posting Permissions

class CanViewGRPOPosting(BasePermission):
    """Permission to view GRPO postings."""

    def has_permission(self, request, view):
        return request.user.has_perm("grpo.can_view_grpo_posting")


class CanCreateGRPOPosting(BasePermission):
    """Permission to create/post GRPO to SAP."""

    def has_permission(self, request, view):
        return request.user.has_perm("grpo.can_create_grpo_posting")


class CanViewPendingGRPO(BasePermission):
    """Permission to view pending GRPO entries."""

    def has_permission(self, request, view):
        return request.user.has_perm("grpo.can_view_pending_grpo")


class CanPreviewGRPO(BasePermission):
    """Permission to preview GRPO data before posting."""

    def has_permission(self, request, view):
        return request.user.has_perm("grpo.can_preview_grpo")


class CanViewGRPOHistory(BasePermission):
    """Permission to view GRPO posting history."""

    def has_permission(self, request, view):
        return request.user.has_perm("grpo.can_view_grpo_history")
