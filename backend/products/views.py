"""
Product views: public listing/detail + admin CRUD.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, parsers, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from parfum.permissions import IsAdmin

from .models import Category, Collection, Product, ProductImage, ProductVariant
from .serializers import (
    CategorySerializer,
    CollectionSerializer,
    ProductDetailSerializer,
    ProductImageSerializer,
    ProductListSerializer,
    ProductVariantSerializer,
    ProductVariantWriteSerializer,
    ProductWriteSerializer,
)


# ──────────────────────────────────────────────────
# PUBLIC ENDPOINTS
# ──────────────────────────────────────────────────


from datetime import timedelta
from django.utils import timezone

class ProductListView(generics.ListAPIView):
    """GET /api/products/ — Browse active products with filtering."""

    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category__slug", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "avg_rating", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("images", "variants")
        )

        # Filter by collection slug
        collection = self.request.query_params.get("collection")
        if collection:
            queryset = queryset.filter(collections__slug=collection)

        # Price range filter (filters on variant prices)
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        if min_price:
            queryset = queryset.filter(variants__price__gte=min_price).distinct()
        if max_price:
            queryset = queryset.filter(variants__price__lte=max_price).distinct()

        return queryset


class NewArrivalsListView(generics.ListAPIView):
    """GET /api/products/new-arrivals/ — Products added in the last 30 days."""

    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return Product.objects.filter(
            is_active=True,
            created_at__gte=thirty_days_ago
        ).select_related("category").prefetch_related(
            "images", "variants"
        ).order_by("-created_at")



class ProductDetailView(generics.RetrieveAPIView):
    """GET /api/products/{slug}/ — Full product detail."""

    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return Product.objects.select_related("category").prefetch_related(
            "collections", "images", "variants", "reviews"
        )


class CategoryListView(generics.ListAPIView):
    """GET /api/categories/ — All categories."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None


class CollectionListView(generics.ListAPIView):
    """GET /api/collections/ — Active collections."""

    queryset = Collection.objects.filter(is_active=True)
    serializer_class = CollectionSerializer
    permission_classes = [AllowAny]
    pagination_class = None


# ──────────────────────────────────────────────────
# ADMIN ENDPOINTS
# ──────────────────────────────────────────────────


class AdminProductViewSet(viewsets.ModelViewSet):
    """CRUD /api/admin/products/ — Admin product management."""

    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "name"]

    def get_queryset(self):
        return Product.objects.select_related("category").prefetch_related(
            "collections", "images", "variants"
        )

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProductWriteSerializer
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        try:
            # Clean up related objects that allow deletion
            product.cart_items.all().delete()
            product.wishlisted_by.all().delete()
            product.reviews.all().delete()
            product.inventory_transfers.all().delete()
            product.images.all().delete()
            product.variants.all().delete()
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {"error": "Cannot delete this product — it has existing orders. Deactivate it instead."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AdminCategoryViewSet(viewsets.ModelViewSet):
    """CRUD /api/admin/categories/ — Admin category management."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class AdminCollectionViewSet(viewsets.ModelViewSet):
    """CRUD /api/admin/collections/ — Admin collection management."""

    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class AdminVariantView(APIView):
    """
    POST /api/admin/products/{product_id}/variants/ — Add variant.
    PUT  /api/admin/products/{product_id}/variants/{variant_id}/ — Update variant.
    DELETE /api/admin/products/{product_id}/variants/{variant_id}/ — Delete variant.
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, product_id):
        """Add a new variant to a product."""
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProductVariantWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check for duplicate ml size
        ml = serializer.validated_data["quantity_ml"]
        if product.variants.filter(quantity_ml=ml).exists():
            return Response(
                {"error": f"A {ml}ml variant already exists for this product."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        variant = serializer.save(product=product)
        return Response(
            ProductVariantSerializer(variant).data,
            status=status.HTTP_201_CREATED,
        )

    def put(self, request, product_id, variant_id=None):
        """Update an existing variant."""
        try:
            variant = ProductVariant.objects.get(pk=variant_id, product_id=product_id)
        except ProductVariant.DoesNotExist:
            return Response(
                {"error": "Variant not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProductVariantWriteSerializer(variant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProductVariantSerializer(variant).data)

    def delete(self, request, product_id, variant_id=None):
        """Delete a variant."""
        try:
            variant = ProductVariant.objects.get(pk=variant_id, product_id=product_id)
        except ProductVariant.DoesNotExist:
            return Response(
                {"error": "Variant not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        variant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductImageUploadView(APIView):
    """POST /api/admin/products/{product_id}/images/ — Upload product image."""

    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        image = request.FILES.get("image")
        if not image:
            return Response(
                {"error": "No image file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        alt_text = request.data.get("alt_text", "")

        # Auto-assign sort_order: next in sequence (0, 1, 2, ...)
        last_order = product.images.order_by("-sort_order").values_list(
            "sort_order", flat=True
        ).first()
        next_order = (last_order + 1) if last_order is not None else 0

        product_image = ProductImage.objects.create(
            product=product,
            image=image,
            alt_text=alt_text,
            sort_order=next_order,
        )

        return Response(
            ProductImageSerializer(product_image).data,
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, product_id):
        """DELETE — remove a product image by image_id query param."""
        image_id = request.query_params.get("image_id")
        if not image_id:
            return Response(
                {"error": "image_id query parameter required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            image = ProductImage.objects.get(pk=image_id, product_id=product_id)
            image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProductImage.DoesNotExist:
            return Response(
                {"error": "Image not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
