"""
Order views: checkout, Razorpay payment, order history, admin management.
"""

import hashlib
import hmac
import logging

import razorpay
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
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
    RazorpayVerifySerializer,
)

logger = logging.getLogger(__name__)

# Initialize Razorpay client (None if keys not configured)
razorpay_client = None
if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


# ──────────────────────────────────────────────────
# CUSTOMER ENDPOINTS
# ──────────────────────────────────────────────────


class CheckoutView(APIView):
    """
    POST /api/orders/checkout/ — Convert cart to order.

    For COD: creates order immediately with pending payment.
    For online payments (UPI/card/wallet/netbanking): creates a Razorpay order
    and returns razorpay_order_id + key_id for frontend to open the popup.
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # ── Get cart ──
        try:
            cart = Cart.objects.prefetch_related(
                "items__product", "items__variant"
            ).get(user=request.user)
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

        # ── Validate stock ──
        errors = []
        for item in cart_items:
            if item.quantity > item.variant.stock:
                errors.append(
                    f"{item.product.name} ({item.variant.quantity_ml}ml): "
                    f"only {item.variant.stock} in stock "
                    f"(requested {item.quantity})"
                )
            if not item.product.is_active:
                errors.append(f"{item.product.name} is no longer available.")

        if errors:
            return Response(
                {"errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Calculate totals ──
        subtotal = sum(item.line_total for item in cart_items)
        discount_amount = 0
        discount_obj = None

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
        is_cod = data["payment_method"] == Payment.Method.COD

        # ── Create Razorpay order (for online payments only) ──
        razorpay_order_id = None
        if not is_cod:
            if not razorpay_client:
                return Response(
                    {"error": "Online payments are not configured. Please use COD."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            try:
                # Razorpay expects amount in paise (INR * 100)
                rz_order = razorpay_client.order.create({
                    "amount": int(total_amount * 100),
                    "currency": "INR",
                    "receipt": f"order_{request.user.pk}_{timezone.now().strftime('%Y%m%d%H%M%S')}",
                    "payment_capture": 1,  # Auto-capture payment
                })
                razorpay_order_id = rz_order["id"]
            except Exception as e:
                logger.error(f"Razorpay order creation failed: {e}")
                return Response(
                    {"error": "Payment gateway error. Please try again."},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

        # ── Create order ──
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

        # ── Create order items & deduct stock ──
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                product_name=item.product.name,
                quantity_ml=item.variant.quantity_ml,
                quantity=item.quantity,
                price_at_purchase=item.variant.effective_price,
            )
            item.variant.stock -= item.quantity
            item.variant.save(update_fields=["stock"])

        # ── Create payment record ──
        payment_status = Payment.Status.PENDING
        if is_cod:
            # COD orders: payment is pending until delivery
            payment_status = Payment.Status.PENDING

        Payment.objects.create(
            order=order,
            method=data["payment_method"],
            amount=total_amount,
            status=payment_status,
            razorpay_order_id=razorpay_order_id,
        )

        # ── Update discount usage ──
        if discount_obj:
            discount_obj.times_used += 1
            discount_obj.save(update_fields=["times_used"])

        # ── Clear cart ──
        # COD: clear immediately (no payment popup needed)
        # Online: keep cart until payment is verified (see VerifyPaymentView)
        if is_cod:
            cart.items.all().delete()

        # ── Build response ──
        response_data = OrderSerializer(order).data

        if not is_cod and razorpay_order_id:
            # Frontend needs these to open Razorpay checkout popup
            response_data["razorpay_order_id"] = razorpay_order_id
            response_data["razorpay_key_id"] = settings.RAZORPAY_KEY_ID
            response_data["amount_paise"] = int(total_amount * 100)
            response_data["currency"] = "INR"

        return Response(response_data, status=status.HTTP_201_CREATED)


class VerifyPaymentView(APIView):
    """
    POST /api/orders/{order_id}/verify-payment/

    After user completes payment in Razorpay popup, frontend sends:
    - razorpay_payment_id
    - razorpay_order_id
    - razorpay_signature

    Backend verifies the HMAC signature to confirm payment is genuine.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        # Validate input
        serializer = RazorpayVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Get order and payment
        try:
            order = Order.objects.get(pk=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            payment = order.payment
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment record not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if already paid
        if payment.status == Payment.Status.COMPLETED:
            return Response(
                {"message": "Payment already verified.", "order": OrderSerializer(order).data}
            )

        # Verify Razorpay signature (HMAC SHA256)
        razorpay_order_id = data["razorpay_order_id"]
        razorpay_payment_id = data["razorpay_payment_id"]
        razorpay_signature = data["razorpay_signature"]

        # Verify the payment belongs to this order
        if payment.razorpay_order_id != razorpay_order_id:
            return Response(
                {"error": "Payment verification failed — order mismatch."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify HMAC signature
        try:
            razorpay_client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            })
        except razorpay.errors.SignatureVerificationError:
            logger.warning(
                f"Razorpay signature verification failed for order {order.pk}"
            )
            payment.status = Payment.Status.FAILED
            payment.save(update_fields=["status"])
            return Response(
                {"error": "Payment verification failed — invalid signature."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Payment verified — mark as completed ──
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.transaction_id = razorpay_payment_id
        payment.status = Payment.Status.COMPLETED
        payment.paid_at = timezone.now()
        payment.save()

        # Update order status
        order.status = Order.Status.CONFIRMED
        order.save(update_fields=["status"])

        # ── Clear cart (deferred from checkout for online payments) ──
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
        except Cart.DoesNotExist:
            pass

        logger.info(f"Payment verified for order {order.pk}: {razorpay_payment_id}")

        return Response({
            "message": "Payment verified successfully!",
            "order": OrderSerializer(order).data,
        })


class RazorpayWebhookView(APIView):
    """
    POST /api/webhooks/razorpay/ — Razorpay webhook handler.

    Backup verification: If frontend fails to call verify-payment,
    Razorpay sends payment.captured event here.

    No auth required (called by Razorpay servers).
    Verified via webhook signature.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        # Verify webhook signature
        webhook_secret = settings.RAZORPAY_KEY_SECRET
        webhook_signature = request.META.get("HTTP_X_RAZORPAY_SIGNATURE", "")
        webhook_body = request.body

        if not webhook_signature:
            return Response(
                {"error": "Missing signature."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # HMAC verification
        expected_signature = hmac.new(
            key=webhook_secret.encode("utf-8"),
            msg=webhook_body,
            digestmod=hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, webhook_signature):
            logger.warning("Razorpay webhook signature mismatch")
            return Response(
                {"error": "Invalid signature."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse event
        event = request.data.get("event")
        payload = request.data.get("payload", {})

        if event == "payment.captured":
            payment_entity = payload.get("payment", {}).get("entity", {})
            rz_order_id = payment_entity.get("order_id")
            rz_payment_id = payment_entity.get("id")

            if rz_order_id:
                try:
                    payment = Payment.objects.get(razorpay_order_id=rz_order_id)
                    if payment.status != Payment.Status.COMPLETED:
                        payment.razorpay_payment_id = rz_payment_id
                        payment.transaction_id = rz_payment_id
                        payment.status = Payment.Status.COMPLETED
                        payment.paid_at = timezone.now()
                        payment.save()

                        # Confirm the order
                        order = payment.order
                        if order.status == Order.Status.PENDING:
                            order.status = Order.Status.CONFIRMED
                            order.save(update_fields=["status"])

                        logger.info(
                            f"Webhook: Payment confirmed for order {order.pk}"
                        )
                except Payment.DoesNotExist:
                    logger.warning(
                        f"Webhook: No payment found for razorpay order {rz_order_id}"
                    )

        elif event == "payment.failed":
            payment_entity = payload.get("payment", {}).get("entity", {})
            rz_order_id = payment_entity.get("order_id")

            if rz_order_id:
                try:
                    payment = Payment.objects.get(razorpay_order_id=rz_order_id)
                    payment.status = Payment.Status.FAILED
                    payment.save(update_fields=["status"])
                    logger.info(
                        f"Webhook: Payment failed for razorpay order {rz_order_id}"
                    )
                except Payment.DoesNotExist:
                    pass

        return Response({"status": "ok"})


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
