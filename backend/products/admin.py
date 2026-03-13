"""
Admin configuration for Products.
"""

from django.contrib import admin

from .models import Category, Collection, Product, ProductImage, ProductVariant, TesterBox


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = [
        "quantity_ml", 
        "india_price", "india_discount_price", "india_stock",
        "switzerland_price", "switzerland_discount_price", "switzerland_stock"
    ]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "avg_rating", "is_active", "is_roll_on", "created_at"]
    list_filter = ["is_active", "is_roll_on", "category", "collections", "created_at"]
    search_fields = ["name", "inspired_by", "description"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductVariantInline, ProductImageInline]
    list_editable = ["is_active", "is_roll_on"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "created_at"]
    list_filter = ["is_active"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = [
        "product", "quantity_ml", 
        "india_price", "india_stock", "switzerland_price", "switzerland_stock"
    ]
    list_filter = ["product"]
    list_editable = ["india_price", "india_stock", "switzerland_price", "switzerland_stock"]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["product", "sort_order", "created_at"]
    list_filter = ["product"]

@admin.register(TesterBox)
class TesterBoxAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "created_at"]
    list_filter = ["is_active"]
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ["products"]
