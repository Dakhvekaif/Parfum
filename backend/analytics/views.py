"""
Analytics views: dashboard stats, sales data, inventory transfers.
"""

from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from orders.serializers import OrderListSerializer
from parfum.permissions import IsAdmin
from products.models import Product

from .models import InventoryTransfer, SalesAnalytics
from .serializers import (
    InventoryTransferSerializer,
    InventoryTransferWriteSerializer,
    SalesAnalyticsSerializer,
)


class DashboardView(APIView):
    """GET /api/admin/analytics/dashboard/ — Aggregated dashboard stats."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        # Revenue & order stats
        order_stats = Order.objects.filter(
            created_at__gte=thirty_days_ago,
            status__in=["confirmed", "shipped", "delivered"],
        ).aggregate(
            total_revenue=Sum("total_amount"),
            total_orders=Count("id"),
        )

        # Counts
        from django.contrib.auth import get_user_model
        User = get_user_model()

        total_customers = User.objects.filter(role="customer").count()
        total_products = Product.objects.filter(is_active=True).count()
        pending_orders = Order.objects.filter(status="pending").count()
        low_stock_products = Product.objects.filter(
            is_active=True, stock__lte=10
        ).count()

        # Recent orders
        recent_orders = Order.objects.order_by("-created_at")[:10]
        recent_orders_data = OrderListSerializer(recent_orders, many=True).data

        # Revenue trend (last 30 days)
        revenue_trend = []
        analytics = SalesAnalytics.objects.filter(
            date__gte=thirty_days_ago.date()
        ).order_by("date")
        for entry in analytics:
            revenue_trend.append({
                "date": entry.date.isoformat(),
                "revenue": str(entry.total_revenue),
                "orders": entry.total_orders,
            })

        return Response({
            "total_revenue": str(order_stats["total_revenue"] or 0),
            "total_orders": order_stats["total_orders"],
            "total_customers": total_customers,
            "total_products": total_products,
            "pending_orders": pending_orders,
            "low_stock_products": low_stock_products,
            "recent_orders": recent_orders_data,
            "revenue_trend": revenue_trend,
        })


class SalesAnalyticsView(generics.ListAPIView):
    """GET /api/admin/analytics/sales/ — Sales data over date range."""

    serializer_class = SalesAnalyticsSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = SalesAnalytics.objects.all()
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        return queryset


class InventoryTransferCreateView(APIView):
    """POST /api/admin/inventory/transfer/ — Record stock in/out."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = InventoryTransferWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            product = Product.objects.get(pk=data["product_id"])
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validate stock out
        if data["transfer_type"] == "out" and product.stock < data["quantity"]:
            return Response(
                {"error": f"Insufficient stock. Current: {product.stock}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create transfer record
        transfer = InventoryTransfer.objects.create(
            product=product,
            admin_user=request.user,
            transfer_type=data["transfer_type"],
            quantity=data["quantity"],
            notes=data.get("notes", ""),
        )

        # Update stock
        if data["transfer_type"] == "in":
            product.stock += data["quantity"]
        else:
            product.stock -= data["quantity"]
        product.save(update_fields=["stock"])

        return Response(
            InventoryTransferSerializer(transfer).data,
            status=status.HTTP_201_CREATED,
        )


class InventoryTransferListView(generics.ListAPIView):
    """GET /api/admin/inventory/transfers/ — Transfer history."""

    serializer_class = InventoryTransferSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = InventoryTransfer.objects.select_related("product", "admin_user")
        product_id = self.request.query_params.get("product_id")
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset
