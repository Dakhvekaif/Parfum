"""
Admin configuration for Analytics.
"""

from django.contrib import admin

from .models import InventoryTransfer, SalesAnalytics


@admin.register(InventoryTransfer)
class InventoryTransferAdmin(admin.ModelAdmin):
    list_display = ["product", "admin_user", "transfer_type", "quantity", "created_at"]
    list_filter = ["transfer_type", "created_at"]
    search_fields = ["product__name", "notes"]


@admin.register(SalesAnalytics)
class SalesAnalyticsAdmin(admin.ModelAdmin):
    list_display = ["date", "total_orders", "total_revenue", "products_sold", "new_customers"]
    list_filter = ["date"]
    ordering = ["-date"]
