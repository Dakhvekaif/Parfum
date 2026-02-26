"""
Custom permissions for Parfum API.
"""

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only allow admin users."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.role == "admin" or request.user.is_superuser)
        )


class IsOwnerOrAdmin(BasePermission):
    """Allow object owner or admin users."""

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin" or request.user.is_superuser:
            return True
        if hasattr(obj, "user"):
            return obj.user == request.user
        return obj == request.user
