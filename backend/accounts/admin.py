"""
Admin configuration for User management.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "first_name", "last_name", "role", "auth_provider", "is_active", "created_at"]
    list_filter = ["role", "auth_provider", "is_active", "created_at"]
    search_fields = ["email", "first_name", "last_name", "phone"]
    ordering = ["-created_at"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "phone")}),
        ("Address", {"fields": ("address", "city", "pincode")}),
        ("Permissions", {"fields": ("role", "auth_provider", "is_active", "is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "password1", "password2", "role"),
        }),
    )
