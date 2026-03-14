from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"admin/products", views.AdminProductViewSet, basename="admin-products")
router.register(r"admin/categories", views.AdminCategoryViewSet, basename="admin-categories")
router.register(r"admin/collections", views.AdminCollectionViewSet, basename="admin-collections")
router.register(r"admin/tester-boxes", views.AdminTesterBoxViewSet, basename="admin-tester-boxes")

urlpatterns = [
    # Public
    path("products/", views.ProductListView.as_view(), name="product-list"),
    path("products/new-arrivals/", views.NewArrivalsListView.as_view(), name="new-arrivals"),
    path("products/migrate-images/", views.MigrateImagesView.as_view(), name="migrate-images"),
    path("products/tester-boxes/", views.TesterBoxListView.as_view(), name="tester-boxes"),
    path("products/top-mens/", views.TopTenMensView.as_view(), name="top-mens"),
    path("products/top-womens/", views.TopTenWomensView.as_view(), name="top-womens"),
    path("products/top-unisex/", views.TopTenUnisexView.as_view(), name="top-unisex"),
    path("products/<slug:slug>/", views.ProductDetailView.as_view(), name="product-detail"),
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path("collections/", views.CollectionListView.as_view(), name="collection-list"),
    path("search/", views.ProductSearchView.as_view(), name="product-search"),
    path("roll-ons/", views.RollOnListView.as_view(), name="roll-on-list"),
    path("roll-ons/top/", views.TopTenRollOnsView.as_view(), name="roll-on-top"),
    path("roll-ons/<slug:slug>/", views.RollOnDetailView.as_view(), name="roll-on-detail"),
    # Admin image upload
    path(
        "admin/products/<int:product_id>/images/",
        views.ProductImageUploadView.as_view(),
        name="product-image-upload",
    ),
    # Admin variant management
    path(
        "admin/products/<int:product_id>/variants/",
        views.AdminVariantView.as_view(),
        name="product-variant-add",
    ),
    path(
        "admin/products/<int:product_id>/variants/<int:variant_id>/",
        views.AdminVariantView.as_view(),
        name="product-variant-detail",
    ),
    # Router
    path("", include(router.urls)),
]
