"""
Admin configuration for Discounts.
"""

from django.contrib import admin

from .models import Discount


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = [
        "code", "discount_type", "value", "min_order_amount",
        "valid_from", "valid_until", "times_used", "usage_limit",
        "is_active", "is_valid",
    ]
    list_filter = ["discount_type", "is_active", "valid_from", "valid_until"]
    search_fields = ["code", "description"]
    list_editable = ["is_active"]
