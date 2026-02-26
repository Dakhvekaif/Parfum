"""
Discount views: apply coupon + admin CRUD.
"""

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from parfum.permissions import IsAdmin

from .models import Discount
from .serializers import DiscountApplySerializer, DiscountSerializer


class DiscountApplyView(APIView):
    """POST /api/discounts/apply/ — Validate and preview coupon discount."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DiscountApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        try:
            discount = Discount.objects.get(code__iexact=code)
        except Discount.DoesNotExist:
            return Response(
                {"error": "Invalid discount code."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not discount.is_valid:
            return Response(
                {"error": "This discount code is expired or no longer valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate preview (using cart total if available)
        from cart.models import Cart
        try:
            cart = Cart.objects.get(user=request.user)
            cart_total = cart.total_price
        except Cart.DoesNotExist:
            cart_total = 0

        if cart_total < discount.min_order_amount:
            return Response(
                {
                    "error": f"Minimum order amount is ₹{discount.min_order_amount}. "
                    f"Your cart total is ₹{cart_total}.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        discount_amount = discount.calculate_discount(cart_total)

        return Response({
            "valid": True,
            "code": discount.code,
            "discount_type": discount.discount_type,
            "value": str(discount.value),
            "discount_amount": str(discount_amount),
            "cart_total": str(cart_total),
            "new_total": str(cart_total - discount_amount),
        })


class AdminDiscountViewSet(viewsets.ModelViewSet):
    """CRUD /api/admin/discounts/ — Admin discount management."""

    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
