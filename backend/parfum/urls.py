"""
Root URL configuration for Parfum backend.
All API endpoints under /api/, admin panel at /admin/.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    """API root — overview of available endpoints."""
    return Response({
        "message": "Welcome to Parfum API 🧴",
        "version": "1.0.0",
        "endpoints": {
            "auth": {
                "register": "/api/auth/register/",
                "login": "/api/auth/login/",
                "logout": "/api/auth/logout/",
                "refresh": "/api/auth/token/refresh/",
                "profile": "/api/auth/profile/",
                "change_password": "/api/auth/change-password/",
            },
            "products": {
                "list": "/api/products/",
                "detail": "/api/products/{slug}/",
                "categories": "/api/categories/",
                "collections": "/api/collections/",
            },
            "cart": {
                "view": "/api/cart/",
                "add": "/api/cart/add/",
                "update": "/api/cart/update/{item_id}/",
                "remove": "/api/cart/remove/{item_id}/",
                "clear": "/api/cart/clear/",
            },
            "wishlist": {
                "list": "/api/wishlist/",
                "toggle": "/api/wishlist/toggle/",
            },
            "orders": {
                "checkout": "/api/orders/checkout/",
                "list": "/api/orders/",
                "detail": "/api/orders/{id}/",
            },
            "reviews": {
                "create": "/api/reviews/",
                "product_reviews": "/api/products/{product_id}/reviews/",
            },
            "discounts": {
                "apply": "/api/discounts/apply/",
            },
            "admin": {
                "dashboard": "/api/admin/analytics/dashboard/",
                "sales": "/api/admin/analytics/sales/",
                "products": "/api/admin/products/",
                "categories": "/api/admin/categories/",
                "collections": "/api/admin/collections/",
                "orders": "/api/admin/orders/",
                "reviews": "/api/admin/reviews/",
                "discounts": "/api/admin/discounts/",
                "inventory_transfer": "/api/admin/inventory/transfer/",
                "inventory_transfers": "/api/admin/inventory/transfers/",
            },
        },
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api_root, name="api-root"),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("products.urls")),
    path("api/", include("cart.urls")),
    path("api/", include("orders.urls")),
    path("api/", include("reviews.urls")),
    path("api/", include("discounts.urls")),
    path("api/", include("analytics.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
