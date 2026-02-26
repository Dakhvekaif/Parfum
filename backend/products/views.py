"""
Product views: public listing/detail + admin CRUD.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, parsers, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from parfum.permissions import IsAdmin

from .models import Category, Collection, Product, ProductImage
from .serializers import (
    CategorySerializer,
    CollectionSerializer,
    ProductDetailSerializer,
    ProductImageSerializer,
    ProductListSerializer,
    ProductWriteSerializer,
)


# ──────────────────────────────────────────────────
# PUBLIC ENDPOINTS
# ──────────────────────────────────────────────────


class ProductListView(generics.ListAPIView):
    """GET /api/products/ — Browse active products with filtering."""

    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category__slug", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at", "avg_rating", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related("category").prefetch_related("images")

        # Filter by collection slug
        collection = self.request.query_params.get("collection")
        if collection:
            queryset = queryset.filter(collections__slug=collection)

        # Price range filter
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    """GET /api/products/{slug}/ — Full product detail."""

    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return Product.objects.select_related("category").prefetch_related(
            "collections", "images", "reviews"
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
    ordering_fields = ["price", "created_at", "stock", "name"]

    def get_queryset(self):
        return Product.objects.select_related("category").prefetch_related(
            "collections", "images"
        )

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProductWriteSerializer
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer


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

        is_primary = request.data.get("is_primary", "false").lower() == "true"
        alt_text = request.data.get("alt_text", "")

        product_image = ProductImage.objects.create(
            product=product,
            image=image,
            alt_text=alt_text,
            is_primary=is_primary,
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
