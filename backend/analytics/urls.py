from django.urls import path

from accounts.views import AdminCustomerListView

from . import views

urlpatterns = [
    path("admin/analytics/dashboard/", views.DashboardView.as_view(), name="admin-dashboard"),
    path("admin/analytics/sales/", views.SalesAnalyticsView.as_view(), name="admin-sales"),
    path("admin/customers/", AdminCustomerListView.as_view(), name="admin-customers"),
    path("admin/inventory/transfer/", views.InventoryTransferCreateView.as_view(), name="inventory-transfer"),
    path("admin/inventory/transfers/", views.InventoryTransferListView.as_view(), name="inventory-transfers"),
]

