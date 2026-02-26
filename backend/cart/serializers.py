"""
Cart and Wishlist serializers.
"""

from rest_framework import serializers

from products.serializers import ProductListSerializer

from .models import Cart, CartItem, Wishlist


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "line_total"]


class CartItemWriteSerializer(serializers.Serializer):
    """For adding/updating cart items."""

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total_items", "total_price", "updated_at"]


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "product", "created_at"]


class WishlistToggleSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
