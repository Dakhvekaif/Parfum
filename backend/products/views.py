"""
Product views: public listing/detail + admin CRUD.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, parsers, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Prefetch

from parfum.permissions import IsAdmin

from .models import Category, Collection, Product, ProductImage, ProductVariant, TesterBox
from .serializers import (
    CategorySerializer,
    CollectionSerializer,
    ProductDetailSerializer,
    ProductImageSerializer,
    ProductListSerializer,
    ProductVariantSerializer,
    ProductVariantWriteSerializer,
    ProductWriteSerializer,
    ProductThumbnailSerializer,
    TesterBoxSerializer,
    AdminTesterBoxWriteSerializer,
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
    search_fields = ["name", "inspired_by"]
    ordering_fields = ["created_at", "avg_rating", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = (
            Product.objects.filter(is_active=True, is_roll_on=False)
            .select_related("category")
            .prefetch_related("images", "variants")
        )

        # Filter by collection slug
        collection = self.request.query_params.get("collection")
        if collection:
            queryset = queryset.filter(collections__slug=collection)

        # Price range filter
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        if min_price or max_price:
            from django.db.models import Q
            
            if min_price:
                queryset = queryset.filter(
                    Q(variants__india_discount_price__isnull=False, variants__india_discount_price__gte=min_price) |
                    Q(variants__india_discount_price__isnull=True, variants__india_price__gte=min_price)
                )
            if max_price:
                queryset = queryset.filter(
                    Q(variants__india_discount_price__isnull=False, variants__india_discount_price__lte=max_price) |
                    Q(variants__india_discount_price__isnull=True, variants__india_price__lte=max_price)
                )
            
            queryset = queryset.distinct()

        return queryset


class NewArrivalsListView(generics.ListAPIView):
    """GET /api/products/new-arrivals/ — Products added in the last 30 days."""

    serializer_class = ProductThumbnailSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return Product.objects.filter(
            is_active=True,
            is_roll_on=False,
            created_at__gte=thirty_days_ago
        ).select_related("category").prefetch_related(
            "images", "variants"
        ).order_by("-created_at")


class TopTenMensView(generics.ListAPIView):
    """GET /api/products/top-mens/ — Top 10 Men's products based on reviews."""
    serializer_class = ProductThumbnailSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True,
            is_roll_on=False,
            category__slug="men"
        ).select_related("category").prefetch_related(
            "images", "variants"
        ).order_by("-avg_rating", "-created_at")[:10]


class TopTenWomensView(generics.ListAPIView):
    """GET /api/products/top-womens/ — Top 10 Women's products based on reviews."""
    serializer_class = ProductThumbnailSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True,
            is_roll_on=False,
            category__slug="women"
        ).select_related("category").prefetch_related(
            "images", "variants"
        ).order_by("-avg_rating", "-created_at")[:10]


class TopTenUnisexView(generics.ListAPIView):
    """GET /api/products/top-unisex/ — Top 10 Unisex products based on reviews."""
    serializer_class = ProductThumbnailSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True,
            is_roll_on=False,
            category__slug="unisex"
        ).select_related("category").prefetch_related(
            "images", "variants"
        ).order_by("-avg_rating", "-created_at")[:10]


class TopTenRollOnsView(generics.ListAPIView):
    """GET /api/roll-ons/top/ — Top 10 Roll-on products based on reviews."""
    serializer_class = ProductThumbnailSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True,
            is_roll_on=True
        ).select_related("category").prefetch_related(
            "images", "variants"
        ).order_by("-avg_rating", "-created_at")[:10]


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


class TesterBoxListView(generics.ListAPIView):
    """GET /api/products/tester-boxes/ — Fetch all active Tester Boxes and their 5ml variants."""

    serializer_class = TesterBoxSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return TesterBox.objects.filter(is_active=True).prefetch_related(
            Prefetch("products", queryset=Product.objects.filter(variants__quantity_ml=5).distinct(), to_attr="prefetched_products_5ml"),
            "products__category", "products__images", "products__variants"
        )


class ProductSearchView(generics.ListAPIView):
    """
    GET /api/search/?q=<query>
    Search active products by name or inspired_by.
    Returns full product detail (variants, images, category, collections).
    """

    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        from django.db.models import Q

        query = self.request.query_params.get("q", "").strip()
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")

        if not query and not min_price and not max_price:
            return Product.objects.none()

        queryset = Product.objects.filter(is_active=True)

        # Text search
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(inspired_by__icontains=query)
            )

        # Price range filter
        if min_price or max_price:
            if min_price:
                queryset = queryset.filter(
                    Q(variants__india_discount_price__isnull=False, variants__india_discount_price__gte=min_price) |
                    Q(variants__india_discount_price__isnull=True, variants__india_price__gte=min_price)
                )
            if max_price:
                queryset = queryset.filter(
                    Q(variants__india_discount_price__isnull=False, variants__india_discount_price__lte=max_price) |
                    Q(variants__india_discount_price__isnull=True, variants__india_price__lte=max_price)
                )

        return (
            queryset
            .select_related("category")
            .prefetch_related("collections", "images", "variants")
            .distinct()
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "query": request.query_params.get("q", "").strip(),
            "min_price": request.query_params.get("min_price"),
            "max_price": request.query_params.get("max_price"),
            "count": queryset.count(),
            "results": serializer.data,
        })


class RollOnListView(generics.ListAPIView):
    """
    GET /api/roll-ons/
    Public listing of all active roll-on attars.
    Always 10ml. Excluded from /api/products/.
    """

    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "inspired_by"]
    ordering_fields = ["created_at", "avg_rating", "name"]
    ordering = ["-created_at"]
    pagination_class = None

    def get_queryset(self):
        return (
            Product.objects.filter(is_active=True, is_roll_on=True)
            .select_related("category")
            .prefetch_related("images", "variants")
        )


class RollOnDetailView(generics.RetrieveAPIView):
    """
    GET /api/roll-ons/{slug}/
    Full detail for a single roll-on product.
    """

    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return Product.objects.filter(is_roll_on=True).select_related(
            "category"
        ).prefetch_related("collections", "images", "variants")


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


class AdminTesterBoxViewSet(viewsets.ModelViewSet):
    """CRUD /api/admin/tester-boxes/ — Admin tester box management."""

    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = TesterBox.objects.prefetch_related("products")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return AdminTesterBoxWriteSerializer
        return TesterBoxSerializer


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

        # Map legacy frontend fields to the new schema
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        
        # Safe fallback for null prices
        if data.get("india_price") in ["", "null", None]:
            data["india_price"] = 0.00
        if data.get("switzerland_price") in ["", "null", None]:
            data["switzerland_price"] = 0.00
            
        if "price" in data and "india_price" not in data:
            try:
                price_val = float(data["price"])
                data["india_price"] = price_val
                data["switzerland_price"] = price_val * 1.2
            except (ValueError, TypeError):
                pass
        if "discount_price" in data and "india_discount_price" not in data:
            data["india_discount_price"] = data["discount_price"]
        if "stock" in data and "india_stock" not in data:
            data["india_stock"] = data["stock"]
            data["switzerland_stock"] = data["stock"]

        serializer = ProductVariantWriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Check for duplicate ml size
        ml = serializer.validated_data.get("quantity_ml")
        if ml and product.variants.filter(quantity_ml=ml).exists():
            return Response(
                {"error": f"A {ml}ml variant already exists for this product."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        variant = serializer.save(product=product)
        return Response(
            ProductVariantSerializer(variant).data,
            status=status.HTTP_201_CREATED,
        )

    def patch(self, request, product_id, variant_id=None):
        """Partial update an existing variant (redirects to put which handles partial)."""
        return self.put(request, product_id, variant_id)

    def put(self, request, product_id, variant_id=None):
        """Update an existing variant."""
        try:
            variant = ProductVariant.objects.get(pk=variant_id, product_id=product_id)
        except ProductVariant.DoesNotExist:
            return Response(
                {"error": "Variant not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Map legacy frontend fields to the new schema
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        
        # Safe fallback for null prices
        if data.get("india_price") in ["", "null", None]:
            data["india_price"] = 0.00
        if data.get("switzerland_price") in ["", "null", None]:
            data["switzerland_price"] = 0.00
            
        if "price" in data and "india_price" not in data:
            try:
                price_val = float(data["price"])
                data["india_price"] = price_val
                data["switzerland_price"] = price_val * 1.2
            except (ValueError, TypeError):
                pass
        if "discount_price" in data and "india_discount_price" not in data:
            if data["discount_price"] in ["", "null", None]:
                data["india_discount_price"] = None
            else:
                data["india_discount_price"] = data["discount_price"]
        if "stock" in data and "india_stock" not in data:
            data["india_stock"] = data["stock"]
            data["switzerland_stock"] = data["stock"]

        serializer = ProductVariantWriteSerializer(variant, data=data, partial=True)
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

    def patch(self, request, product_id):
        """PATCH — set an image as primary by image_id query param."""
        image_id = request.query_params.get("image_id")
        if not image_id:
            return Response(
                {"error": "image_id query parameter required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            from django.db.models import F
            image = ProductImage.objects.get(pk=image_id, product_id=product_id)
            # Push all other images down
            ProductImage.objects.filter(product_id=product_id).exclude(pk=image_id).update(sort_order=F('sort_order') + 1)
            # Set this image as primary
            image.sort_order = 0
            image.save(update_fields=["sort_order"])
            return Response({"message": "Image set as primary."}, status=status.HTTP_200_OK)
        except ProductImage.DoesNotExist:
            return Response({"error": "Image not found."}, status=status.HTTP_404_NOT_FOUND)

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


class MigrateImagesView(APIView):
    """Temporary endpoint to migrate images to Cloudinary on Render."""
    
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            import urllib.request
            from django.core.files.base import ContentFile
            from products.models import Product, ProductImage
            from products.management.commands.seed_data import PRODUCT_IMAGES

            ProductImage.objects.all().delete()
            products = Product.objects.all()
            images_created = 0

            for product in products:
                urls = PRODUCT_IMAGES.get(product.name, [])
                for sort_order, url in enumerate(urls):
                    try:
                        req = urllib.request.Request(
                            url,
                            headers={'User-Agent': 'SwissAroma-Seeder/1.0'},
                        )
                        response = urllib.request.urlopen(req, timeout=15)
                        image_data = response.read()

                        slug = product.slug or product.name.lower().replace(' ', '-')
                        filename = f'{slug}-{sort_order + 1}.jpg'

                        product_image = ProductImage(
                            product=product,
                            alt_text=f'{product.name} - Image {sort_order + 1}',
                            sort_order=sort_order,
                        )
                        product_image.image.save(
                            filename,
                            ContentFile(image_data),
                            save=True,
                        )
                        images_created += 1
                    except Exception as inner_e:
                        pass

            return Response({"message": f"Successfully migrated {images_created} images to Cloudinary!"})
        except Exception as e:
            import traceback
            return Response(
                {"error": str(e), "traceback": traceback.format_exc()},
                status=500
            )
