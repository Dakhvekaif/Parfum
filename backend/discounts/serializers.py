"""
Discount serializers.
"""

from rest_framework import serializers

from .models import Discount


class DiscountSerializer(serializers.ModelSerializer):
    is_valid = serializers.ReadOnlyField()

    class Meta:
        model = Discount
        fields = [
            "id", "code", "description", "discount_type", "value",
            "min_order_amount", "max_discount_amount",
            "valid_from", "valid_until",
            "usage_limit", "times_used", "is_active", "is_valid",
            "created_at",
        ]
        read_only_fields = ["id", "times_used", "created_at"]


class DiscountApplySerializer(serializers.Serializer):
    """Validate and apply a coupon code."""
    code = serializers.CharField(max_length=50)
