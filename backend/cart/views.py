"""
Cart and Wishlist views.
"""

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .models import Cart, CartItem, Wishlist
from .serializers import (
    CartItemWriteSerializer,
    CartSerializer,
    WishlistSerializer,
    WishlistToggleSerializer,
)


class CartView(APIView):
    """GET /api/cart/ — View current cart with all items."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartAddView(APIView):
    """POST /api/cart/add/ — Add product to cart or update quantity if exists."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CartItemWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]

        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found or inactive."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if product.stock < quantity:
            return Response(
                {"error": f"Only {product.stock} items in stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )

        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > product.stock:
                return Response(
                    {"error": f"Cannot add more. Only {product.stock} in stock."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            cart_item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class CartUpdateView(APIView):
    """PUT /api/cart/update/{item_id}/ — Update cart item quantity."""

    permission_classes = [IsAuthenticated]

    def put(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(
                pk=item_id, cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        quantity = request.data.get("quantity")
        if not quantity or int(quantity) < 1:
            return Response(
                {"error": "Quantity must be at least 1."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        quantity = int(quantity)
        if quantity > cart_item.product.stock:
            return Response(
                {"error": f"Only {cart_item.product.stock} items in stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_item.quantity = quantity
        cart_item.save()

        return Response(CartSerializer(cart_item.cart).data)


class CartRemoveView(APIView):
    """DELETE /api/cart/remove/{item_id}/ — Remove item from cart."""

    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(
                pk=item_id, cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart = cart_item.cart
        cart_item.delete()
        return Response(CartSerializer(cart).data)


class CartClearView(APIView):
    """DELETE /api/cart/clear/ — Empty entire cart."""

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response(CartSerializer(cart).data)


# ──────────────────────────────────────────────────
# WISHLIST
# ──────────────────────────────────────────────────


class WishlistView(generics.ListAPIView):
    """GET /api/wishlist/ — View wishlist."""

    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related(
            "product__category"
        ).prefetch_related("product__images")


class WishlistToggleView(APIView):
    """POST /api/wishlist/toggle/ — Add/remove product from wishlist."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WishlistToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user, product=product
        )

        if not created:
            wishlist_item.delete()
            return Response(
                {"message": "Removed from wishlist.", "wishlisted": False}
            )

        return Response(
            {"message": "Added to wishlist.", "wishlisted": True},
            status=status.HTTP_201_CREATED,
        )
