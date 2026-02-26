"""
Admin configuration for Reviews.
"""

from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "product", "rating", "is_approved", "created_at"]
    list_filter = ["is_approved", "rating", "created_at"]
    search_fields = ["user__email", "product__name", "comment"]
    list_editable = ["is_approved"]

    actions = ["approve_reviews", "reject_reviews"]

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Reject (delete) selected reviews")
    def reject_reviews(self, request, queryset):
        queryset.delete()
