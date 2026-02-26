"""
Order views: checkout, order history, admin order management, payments.
"""

from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart
from discounts.models import Discount
from parfum.permissions import IsAdmin

from .models import Order, OrderItem, Payment
from .serializers import (
    CheckoutSerializer,
    OrderListSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
    PaymentCreateSerializer,
)


class CheckoutView(APIView):
    """POST /api/orders/checkout/ — Convert cart to order with stock validation."""

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Get cart
        try:
            cart = Cart.objects.prefetch_related("items__product").get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_items = cart.items.all()
        if not cart_items.exists():
            return Response(
                {"error": "Cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate stock for all items
        errors = []
        for item in cart_items:
            if item.quantity > item.product.stock:
                errors.append(
                    f"{item.product.name}: only {item.product.stock} in stock "
                    f"(requested {item.quantity})"
                )
            if not item.product.is_active:
                errors.append(f"{item.product.name} is no longer available.")

        if errors:
            return Response(
                {"errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate totals
        subtotal = sum(item.line_total for item in cart_items)
        discount_amount = 0
        discount_obj = None

        # Apply discount code if provided
        discount_code = data.get("discount_code", "").strip()
        if discount_code:
            try:
                discount_obj = Discount.objects.get(code__iexact=discount_code)
                if not discount_obj.is_valid:
                    return Response(
                        {"error": "Discount code is expired or invalid."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                discount_amount = discount_obj.calculate_discount(subtotal)
            except Discount.DoesNotExist:
                return Response(
                    {"error": "Invalid discount code."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        total_amount = subtotal - discount_amount

        # Create order
        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            discount_amount=discount_amount,
            total_amount=total_amount,
            shipping_name=data["shipping_name"],
            shipping_address=data["shipping_address"],
            shipping_city=data["shipping_city"],
            shipping_pincode=data["shipping_pincode"],
            shipping_phone=data["shipping_phone"],
            discount_code=discount_obj,
            status=Order.Status.PENDING,
        )

        # Create order items (snapshot) & deduct stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                quantity=item.quantity,
                price_at_purchase=item.product.effective_price,
            )
            # Deduct stock
            item.product.stock -= item.quantity
            item.product.save(update_fields=["stock"])

        # Create payment record
        Payment.objects.create(
            order=order,
            method=data["payment_method"],
            amount=total_amount,
            status=Payment.Status.PENDING,
        )

        # Update discount usage
        if discount_obj:
            discount_obj.times_used += 1
            discount_obj.save(update_fields=["times_used"])

        # Clear cart
        cart.items.all().delete()

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class OrderListView(generics.ListAPIView):
    """GET /api/orders/ — User's order history."""

    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    """GET /api/orders/{id}/ — Single order detail."""

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_admin:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)


# ──────────────────────────────────────────────────
# ADMIN ENDPOINTS
# ──────────────────────────────────────────────────


class AdminOrderListView(generics.ListAPIView):
    """GET /api/admin/orders/ — All orders for admin."""

    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = Order.objects.all()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class AdminOrderStatusView(APIView):
    """PUT /api/admin/orders/{id}/status/ — Update order status."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order.status = serializer.validated_data["status"]
        if serializer.validated_data.get("tracking_id"):
            order.tracking_id = serializer.validated_data["tracking_id"]
        if serializer.validated_data.get("notes"):
            order.notes = serializer.validated_data["notes"]
        order.save()

        # If order is confirmed/shipped, mark payment as completed
        if order.status in [Order.Status.CONFIRMED, Order.Status.SHIPPED]:
            try:
                payment = order.payment
                if payment.status == Payment.Status.PENDING:
                    payment.status = Payment.Status.COMPLETED
                    payment.paid_at = timezone.now()
                    payment.save()
            except Payment.DoesNotExist:
                pass

        return Response(OrderSerializer(order).data)


class PaymentUpdateView(APIView):
    """POST /api/orders/{order_id}/payment/ — Record/update payment info."""

    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payment = order.payment
        except Payment.DoesNotExist:
            return Response(
                {"error": "No payment record found for this order."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payment.transaction_id = serializer.validated_data["transaction_id"]
        payment.method = serializer.validated_data["method"]
        payment.save()

        return Response(OrderSerializer(order).data)
