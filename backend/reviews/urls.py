from django.urls import path

from . import views

urlpatterns = [
    # Public
    path("products/<int:product_id>/reviews/", views.ProductReviewsView.as_view(), name="product-reviews"),
    # Customer
    path("reviews/", views.CreateReviewView.as_view(), name="create-review"),
    # Admin
    path("admin/reviews/", views.AdminReviewListView.as_view(), name="admin-review-list"),
    path("admin/reviews/<int:pk>/approve/", views.AdminReviewApproveView.as_view(), name="admin-review-approve"),
]
