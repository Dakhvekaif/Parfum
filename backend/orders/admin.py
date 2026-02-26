"""
Admin configuration for Orders and Payments.
"""

from django.contrib import admin

from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product_name", "quantity", "price_at_purchase", "line_total"]


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "user", "status", "total_amount", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["order_number", "user__email", "tracking_id"]
    readonly_fields = ["order_number", "subtotal", "discount_amount", "total_amount"]
    inlines = [OrderItemInline, PaymentInline]

    actions = ["mark_confirmed", "mark_shipped", "mark_delivered"]

    @admin.action(description="Mark selected orders as Confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.update(status=Order.Status.CONFIRMED)

    @admin.action(description="Mark selected orders as Shipped")
    def mark_shipped(self, request, queryset):
        queryset.update(status=Order.Status.SHIPPED)

    @admin.action(description="Mark selected orders as Delivered")
    def mark_delivered(self, request, queryset):
        queryset.update(status=Order.Status.DELIVERED)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["order", "method", "amount", "status", "transaction_id", "created_at"]
    list_filter = ["status", "method"]
    search_fields = ["transaction_id"]
