"""
Analytics models: InventoryTransfer and SalesAnalytics.
"""

from django.conf import settings
from django.db import models


class InventoryTransfer(models.Model):
    """Track stock in/out movements with admin attribution."""

    class TransferType(models.TextChoices):
        IN = "in", "Stock In"
        OUT = "out", "Stock Out"

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="inventory_transfers",
    )
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="inventory_transfers",
    )
    transfer_type = models.CharField(max_length=3, choices=TransferType.choices)
    quantity = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        direction = "+" if self.transfer_type == "in" else "-"
        return f"{direction}{self.quantity} {self.product.name}"


class SalesAnalytics(models.Model):
    """Daily aggregated metrics for admin dashboard."""

    date = models.DateField(unique=True, db_index=True)
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    products_sold = models.PositiveIntegerField(default=0)
    new_customers = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "sales analytics"
        ordering = ["-date"]

    def __str__(self):
        return f"Analytics {self.date} — ₹{self.total_revenue} ({self.total_orders} orders)"
