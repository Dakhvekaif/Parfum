"""
Order and Payment models.
Orders use header-detail pattern: Order → OrderItems.
OrderItems preserve priceAtPurchase for historical accuracy.
"""

import uuid

from django.conf import settings
from django.db import models


class Order(models.Model):
    """Order header with user, status tracking, amounts, and shipping."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    # Use UUID for order number (secure, non-guessable)
    order_number = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Shipping — snapshot at time of order
    shipping_name = models.CharField(max_length=200)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_pincode = models.CharField(max_length=10)
    shipping_phone = models.CharField(max_length=15)

    # Tracking
    tracking_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    # Discount reference
    discount_code = models.ForeignKey(
        "discounts.Discount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"Order {self.order_number} — {self.get_status_display()}"


class OrderItem(models.Model):
    """
    Snapshot of product at time of purchase.
    priceAtPurchase ensures historical accuracy even if product price changes later.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    # Snapshot fields — preserved from time of purchase
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.quantity}x {self.product_name} @ ₹{self.price_at_purchase}"

    @property
    def line_total(self):
        return self.price_at_purchase * self.quantity


class Payment(models.Model):
    """Payment tracking for orders. Supports UPI, digital wallets, COD."""

    class Method(models.TextChoices):
        UPI = "upi", "UPI"
        WALLET = "wallet", "Digital Wallet"
        COD = "cod", "Cash on Delivery"
        CARD = "card", "Credit/Debit Card"
        NETBANKING = "netbanking", "Net Banking"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
    )
    method = models.CharField(max_length=15, choices=Method.choices)
    transaction_id = models.CharField(
        max_length=200, blank=True, unique=True, null=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id or 'N/A'} — {self.get_status_display()}"
