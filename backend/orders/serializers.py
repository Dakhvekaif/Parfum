"""
Order and Payment serializers.
"""

from rest_framework import serializers

from .models import Order, OrderItem, Payment


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = [
            "id", "product", "product_name", "quantity",
            "price_at_purchase", "line_total",
        ]
        read_only_fields = fields


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "method", "transaction_id", "amount",
            "status", "paid_at", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class OrderSerializer(serializers.ModelSerializer):
    """Full order detail with items and payment."""

    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "status", "status_display",
            "subtotal", "discount_amount", "total_amount",
            "shipping_name", "shipping_address", "shipping_city",
            "shipping_pincode", "shipping_phone",
            "tracking_id", "notes", "discount_code",
            "items", "payment",
            "created_at", "updated_at",
        ]
        read_only_fields = fields


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight order list."""

    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    item_count = serializers.IntegerField(source="items.count", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "status", "status_display",
            "total_amount", "item_count", "created_at",
        ]


class CheckoutSerializer(serializers.Serializer):
    """Checkout from cart → order."""

    shipping_name = serializers.CharField(max_length=200)
    shipping_address = serializers.CharField()
    shipping_city = serializers.CharField(max_length=100)
    shipping_pincode = serializers.CharField(max_length=10)
    shipping_phone = serializers.CharField(max_length=15)
    payment_method = serializers.ChoiceField(choices=Payment.Method.choices)
    discount_code = serializers.CharField(max_length=50, required=False, allow_blank=True)


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Admin: update order status."""

    status = serializers.ChoiceField(choices=Order.Status.choices)
    tracking_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class PaymentCreateSerializer(serializers.Serializer):
    """Record a payment for an order."""

    transaction_id = serializers.CharField(max_length=200)
    method = serializers.ChoiceField(choices=Payment.Method.choices)
