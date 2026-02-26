"""
Analytics serializers.
"""

from rest_framework import serializers

from .models import InventoryTransfer, SalesAnalytics


class InventoryTransferSerializer(serializers.ModelSerializer):
    admin_email = serializers.EmailField(source="admin_user.email", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = InventoryTransfer
        fields = [
            "id", "product", "product_name", "admin_user", "admin_email",
            "transfer_type", "quantity", "notes", "created_at",
        ]
        read_only_fields = ["id", "admin_user", "created_at"]


class InventoryTransferWriteSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    transfer_type = serializers.ChoiceField(choices=InventoryTransfer.TransferType.choices)
    quantity = serializers.IntegerField(min_value=1)
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class SalesAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesAnalytics
        fields = [
            "id", "date", "total_orders", "total_revenue",
            "products_sold", "new_customers",
        ]


class DashboardSerializer(serializers.Serializer):
    """Aggregated dashboard stats."""

    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    total_products = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    low_stock_products = serializers.IntegerField()
    recent_orders = serializers.ListField()
    revenue_trend = serializers.ListField()
