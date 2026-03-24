"""
Cart and Wishlist serializers.
"""

from rest_framework import serializers

from products.serializers import ProductListSerializer, ProductThumbnailSerializer, ProductVariantSerializer

from .models import Cart, CartItem, Wishlist


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    line_total = serializers.ReadOnlyField()

    selected_origin = serializers.CharField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "variant", "quantity", "line_total", "selected_origin", "tester_box_items"]


class CartItemWriteSerializer(serializers.Serializer):
    """For adding/updating cart items — now uses variant_id."""

    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    selected_origin = serializers.ChoiceField(
        choices=[("india", "India"), ("switzerland", "Switzerland")],
        default="india"
    )
    tester_box_items = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list
    )


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total_items", "total_price", "updated_at"]


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductThumbnailSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "product", "created_at"]


class WishlistToggleSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
