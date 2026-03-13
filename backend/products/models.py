"""
Product models: Category, Collection, Product, ProductVariant, ProductImage.
"""

from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Product categories like 'Men', 'Women', 'Unisex'."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Collection(models.Model):
    """Curated product groups like 'Indian Products', 'Swiss Products'."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="collections/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class TesterBox(models.Model):
    """Admin-managed groups of products for tester boxes."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    products = models.ManyToManyField(
        "Product",
        related_name="tester_boxes",
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "tester boxes"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Core product — name, description, category. Pricing lives in variants."""

    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    inspired_by = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g. 'Our Creation Of Bdk\\'s Vanille Leather Perfume'"
    )
    description = models.TextField()
    avg_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00,
    )
    is_active = models.BooleanField(default=True, db_index=True)
    is_roll_on = models.BooleanField(
        default=False, db_index=True,
        help_text="If True, this product is a roll-on attar and will not appear in the main product listing.",
    )

    # Relationships
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    collections = models.ManyToManyField(
        Collection,
        related_name="products",
        blank=True,
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["category", "is_active"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def starting_price(self):
        """Returns the lowest effective price across all variants (for listings)."""
        variant = self.variants.order_by("india_price").first()
        if variant:
            return variant.india_effective_price
        return None

    @property
    def in_stock(self):
        """True if any variant has stock."""
        from django.db.models import Q
        return self.variants.filter(Q(india_stock__gt=0) | Q(switzerland_stock__gt=0)).exists()


class ProductVariant(models.Model):
    """Size/ML variant with its own price and stock."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )
    quantity_ml = models.PositiveIntegerField(
        help_text="Bottle size in millilitres (e.g. 10, 30, 50)",
    )
    india_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0.00,
        help_text="Price for India variant",
    )
    india_discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        help_text="Discount price for India variant",
    )
    switzerland_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0.00,
        help_text="Price for Switzerland variant",
    )
    switzerland_discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        help_text="Discount price for Switzerland variant",
    )
    india_stock = models.PositiveIntegerField(default=0, help_text="Stock for India variant")
    switzerland_stock = models.PositiveIntegerField(default=0, help_text="Stock for Switzerland variant")

    class Meta:
        ordering = ["quantity_ml"]
        unique_together = ("product", "quantity_ml")

    def __str__(self):
        return f"{self.product.name} — {self.quantity_ml}ml"

    # -- India Properties --
    @property
    def india_effective_price(self):
        return self.india_discount_price if self.india_discount_price else self.india_price

    @property
    def india_discount_percentage(self):
        if self.india_discount_price and self.india_price > 0:
            return round(((self.india_price - self.india_discount_price) / self.india_price) * 100)
        return 0

    # -- Switzerland Properties --
    @property
    def switzerland_effective_price(self):
        return self.switzerland_discount_price if self.switzerland_discount_price else self.switzerland_price

    @property
    def switzerland_discount_percentage(self):
        if self.switzerland_discount_price and self.switzerland_price > 0:
            return round(((self.switzerland_price - self.switzerland_discount_price) / self.switzerland_price) * 100)
        return 0

    @property
    def in_stock(self):
        return self.india_stock > 0 or self.switzerland_stock > 0

    @property
    def india_in_stock(self):
        return self.india_stock > 0

    @property
    def switzerland_in_stock(self):
        return self.switzerland_stock > 0


class ProductImage(models.Model):
    """Multiple images per product. Image with sort_order 0 is the main image."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"Image for {self.product.name} (order: {self.sort_order})"
