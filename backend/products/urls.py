from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"admin/products", views.AdminProductViewSet, basename="admin-products")
router.register(r"admin/categories", views.AdminCategoryViewSet, basename="admin-categories")
router.register(r"admin/collections", views.AdminCollectionViewSet, basename="admin-collections")

urlpatterns = [
    # Public
    path("products/", views.ProductListView.as_view(), name="product-list"),
    path("products/<slug:slug>/", views.ProductDetailView.as_view(), name="product-detail"),
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path("collections/", views.CollectionListView.as_view(), name="collection-list"),
    # Admin image upload
    path(
        "admin/products/<int:product_id>/images/",
        views.ProductImageUploadView.as_view(),
        name="product-image-upload",
    ),
    # Router
    path("", include(router.urls)),
]
