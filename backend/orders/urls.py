from django.urls import path

from . import views

urlpatterns = [
    # Customer
    path("orders/checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("orders/buy-now/", views.BuyNowView.as_view(), name="buy-now"),
    path("orders/cart-preview/", views.CartPricingPreviewView.as_view(), name="cart-preview"),
    path("orders/buynow-preview/", views.BuyNowPricingPreviewView.as_view(), name="buynow-preview"),
    path("orders/", views.OrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:order_id>/verify-payment/", views.VerifyPaymentView.as_view(), name="verify-payment"),
    path("orders/<int:order_id>/payment/", views.PaymentUpdateView.as_view(), name="payment-update"),
    # Razorpay webhook (no auth — called by Razorpay servers)
    path("webhooks/razorpay/", views.RazorpayWebhookView.as_view(), name="razorpay-webhook"),
    # Admin
    path("admin/orders/", views.AdminOrderListView.as_view(), name="admin-order-list"),
    path("admin/orders/<int:pk>/status/", views.AdminOrderStatusView.as_view(), name="admin-order-status"),
]
