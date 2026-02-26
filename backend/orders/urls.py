from django.urls import path

from . import views

urlpatterns = [
    # Customer
    path("orders/checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("orders/", views.OrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:order_id>/payment/", views.PaymentUpdateView.as_view(), name="payment-update"),
    # Admin
    path("admin/orders/", views.AdminOrderListView.as_view(), name="admin-order-list"),
    path("admin/orders/<int:pk>/status/", views.AdminOrderStatusView.as_view(), name="admin-order-status"),
]
