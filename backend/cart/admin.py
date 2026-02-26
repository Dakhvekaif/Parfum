"""
Admin configuration for Cart and Wishlist.
"""

from django.contrib import admin

from .models import Cart, CartItem, Wishlist


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ["line_total"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["user", "total_items", "total_price", "updated_at"]
    inlines = [CartItemInline]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ["user", "product", "created_at"]
    list_filter = ["created_at"]
