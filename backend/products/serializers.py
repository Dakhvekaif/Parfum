"""
Product serializers with nested images, categories, and collections.
"""

from rest_framework import serializers

from .models import Category, Collection, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(source="products.count", read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "image", "product_count"]
        read_only_fields = ["slug"]


class CollectionSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(source="products.count", read_only=True)

    class Meta:
        model = Collection
        fields = [
            "id", "name", "slug", "description", "image",
            "is_active", "product_count",
        ]
        read_only_fields = ["slug"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "is_primary", "sort_order"]


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings."""

    category = CategorySerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    effective_price = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "price", "discount_price",
            "effective_price", "discount_percentage", "stock", "in_stock",
            "avg_rating", "is_active", "category", "primary_image", "created_at",
        ]

    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if not primary:
            primary = obj.images.first()
        if primary:
            return ProductImageSerializer(primary).data
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full product detail with all images, categories, collections."""

    category = CategorySerializer(read_only=True)
    collections = CollectionSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    effective_price = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "description", "price", "discount_price",
            "effective_price", "discount_percentage", "stock", "in_stock",
            "avg_rating", "is_active", "category", "collections", "images",
            "created_at", "updated_at",
        ]


class ProductWriteSerializer(serializers.ModelSerializer):
    """Admin serializer for creating/updating products."""

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category",
    )
    collection_ids = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(), source="collections",
        many=True, required=False,
    )

    class Meta:
        model = Product
        fields = [
            "id", "name", "description", "price", "discount_price",
            "stock", "is_active", "category_id", "collection_ids",
        ]

    def create(self, validated_data):
        collections = validated_data.pop("collections", [])
        product = Product.objects.create(**validated_data)
        product.collections.set(collections)
        return product

    def update(self, instance, validated_data):
        collections = validated_data.pop("collections", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if collections is not None:
            instance.collections.set(collections)
        return instance
