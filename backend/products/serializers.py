"""
Product serializers with nested variants, images, categories, and collections.
"""

from rest_framework import serializers

from .models import Category, Collection, Product, ProductImage, ProductVariant, TesterBox


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
        fields = ["id", "image", "alt_text", "sort_order"]


class ProductVariantSerializer(serializers.ModelSerializer):
    """Variant with size, pricing, and stock info."""

    india_effective_price = serializers.ReadOnlyField()
    india_discount_percentage = serializers.ReadOnlyField()
    switzerland_effective_price = serializers.ReadOnlyField()
    switzerland_discount_percentage = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()
    india_in_stock = serializers.ReadOnlyField()
    switzerland_in_stock = serializers.ReadOnlyField()

    class Meta:
        model = ProductVariant
        fields = [
            "id", "quantity_ml",
            "india_price", "india_discount_price", "india_effective_price", "india_discount_percentage",
            "switzerland_price", "switzerland_discount_price", "switzerland_effective_price", "switzerland_discount_percentage",
            "india_stock", "india_in_stock",
            "switzerland_stock", "switzerland_in_stock",
            "in_stock", "oversell",
        ]


class TesterBoxVariantSerializer(serializers.ModelSerializer):
    """Ultra-lightweight variant for Tester Boxes (No Prices)."""

    in_stock = serializers.ReadOnlyField()
    india_in_stock = serializers.ReadOnlyField()
    switzerland_in_stock = serializers.ReadOnlyField()

    class Meta:
        model = ProductVariant
        fields = [
            "id", "quantity_ml",
            "india_stock", "india_in_stock",
            "switzerland_stock", "switzerland_in_stock",
            "in_stock", "oversell",
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings."""

    category = CategorySerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()
    starting_price = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "inspired_by", "starting_price",
            "in_stock", "avg_rating", "is_active", "is_roll_on", "category",
            "primary_image", "variants", "created_at",
        ]

    def get_primary_image(self, obj):
        """Returns the first image by sort_order as the main image."""
        first_image = obj.images.first()  # already ordered by sort_order
        if first_image:
            return ProductImageSerializer(first_image).data
        return None

    def get_variants(self, obj):
        # Exclude 5ml variants from the main listing
        filtered_variants = [v for v in obj.variants.all() if v.quantity_ml != 5]
        return ProductVariantSerializer(filtered_variants, many=True).data


class ProductThumbnailSerializer(serializers.ModelSerializer):
    """Ultra-lightweight serializer for product thumbnails (Home, Top 10, etc.)."""

    category = CategorySerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    starting_price = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "inspired_by", "category",
            "avg_rating", "starting_price", "primary_image",
        ]

    def get_primary_image(self, obj):
        """Returns the first image by sort_order as the main image."""
        first_image = obj.images.first()
        if first_image:
            return ProductImageSerializer(first_image).data
        return None


class TesterBoxItemSerializer(serializers.ModelSerializer):
    """Serialize the individual products inside a TesterBox."""
    category = CategorySerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()
    starting_price = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "inspired_by", "starting_price",
            "in_stock", "avg_rating", "is_active", "category",
            "primary_image", "variants", "created_at",
        ]

    def get_primary_image(self, obj):
        first_image = obj.images.filter(sort_order=0).first()
        if first_image:
            return ProductImageSerializer(first_image).data
        return None

    def get_variants(self, obj):
        tester_variants = [v for v in obj.variants.all() if v.quantity_ml == 5]
        return TesterBoxVariantSerializer(tester_variants, many=True).data

class TesterBoxSerializer(serializers.ModelSerializer):
    """Public read-only serializer for Tester Boxes and their 5ml products."""
    products = TesterBoxItemSerializer(many=True, read_only=True)

    class Meta:
        model = TesterBox
        fields = ["id", "name", "slug", "description", "products", "created_at"]
        read_only_fields = ["slug", "created_at"]

class AdminTesterBoxWriteSerializer(serializers.ModelSerializer):
    """Admin writes tester boxes with related product IDs."""
    product_ids = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(variants__quantity_ml=5).distinct(), source="products",
        many=True, required=False,
    )

    class Meta:
        model = TesterBox
        fields = ["id", "name", "description", "is_active", "product_ids"]

    def create(self, validated_data):
        products = validated_data.pop("products", [])
        tester_box = TesterBox.objects.create(**validated_data)
        tester_box.products.set(products)
        return tester_box

    def update(self, instance, validated_data):
        products = validated_data.pop("products", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if products is not None:
            instance.products.set(products)
        return instance


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full product detail with all images, variants, categories, collections."""

    category = CategorySerializer(read_only=True)
    collections = CollectionSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = serializers.SerializerMethodField()
    starting_price = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "inspired_by", "description",
            "starting_price", "in_stock", "avg_rating", "is_active", "is_roll_on",
            "category", "collections", "images", "variants",
            "created_at", "updated_at",
        ]

    def get_variants(self, obj):
        # Exclude 5ml variants from the details
        filtered_variants = [v for v in obj.variants.all() if v.quantity_ml != 5]
        return ProductVariantSerializer(filtered_variants, many=True).data


class ProductWriteSerializer(serializers.ModelSerializer):
    """Admin serializer for creating/updating products (without variants)."""

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
            "id", "name", "inspired_by", "description", "is_active", "is_roll_on",
            "category_id", "collection_ids",
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


class ProductVariantWriteSerializer(serializers.ModelSerializer):
    """Admin serializer for creating/updating product variants."""

    class Meta:
        model = ProductVariant
        fields = [
            "id", "quantity_ml", 
            "india_price", "india_discount_price", "india_stock",
            "switzerland_price", "switzerland_discount_price", "switzerland_stock",
            "oversell",
        ]
