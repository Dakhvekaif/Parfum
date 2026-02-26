"""
Discount/Coupon model with percentage/fixed discounts, validity periods, usage limits.
"""

from django.db import models
from django.utils import timezone


class Discount(models.Model):
    """Coupon codes with configurable discount rules."""

    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "Percentage"
        FIXED = "fixed", "Fixed Amount"

    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(
        max_length=10,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE,
    )
    value = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Percentage (e.g., 10 for 10%) or fixed amount in ₹",
    )
    min_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Minimum order amount to apply this discount",
    )
    max_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        help_text="Maximum discount cap (for percentage discounts)",
    )
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(
        default=0,
        help_text="0 = unlimited usage",
    )
    times_used = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} — {self.value}{'%' if self.discount_type == 'percentage' else '₹'}"

    @property
    def is_valid(self):
        """Check if coupon is currently valid."""
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.usage_limit > 0 and self.times_used >= self.usage_limit:
            return False
        return True

    def calculate_discount(self, order_total):
        """Calculate discount amount for a given order total."""
        if order_total < self.min_order_amount:
            return 0

        if self.discount_type == self.DiscountType.PERCENTAGE:
            discount = (self.value / 100) * order_total
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
        else:
            discount = self.value

        return min(discount, order_total)  # Never exceed order total
