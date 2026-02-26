"""
Review views with admin approval workflow.
"""

from django.db.models import Avg
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from parfum.permissions import IsAdmin
from products.models import Product

from .models import Review
from .serializers import ReviewSerializer


class ProductReviewsView(generics.ListAPIView):
    """GET /api/products/{product_id}/reviews/ — Approved reviews for a product."""

    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Review.objects.filter(
            product_id=self.kwargs["product_id"],
            is_approved=True,
        ).select_related("user")


class CreateReviewView(APIView):
    """POST /api/reviews/ — Submit a review (auto-pending for approval)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = request.data.get("product")
        # Check if user already reviewed this product
        if Review.objects.filter(user=request.user, product_id=product_id).exists():
            return Response(
                {"error": "You have already reviewed this product."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        review = serializer.save(user=request.user)
        return Response(
            {
                "message": "Review submitted. It will be visible after admin approval.",
                "review": ReviewSerializer(review).data,
            },
            status=status.HTTP_201_CREATED,
        )


class AdminReviewListView(generics.ListAPIView):
    """GET /api/admin/reviews/ — All reviews (pending + approved)."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = Review.objects.select_related("user", "product")
        approved = self.request.query_params.get("approved")
        if approved is not None:
            queryset = queryset.filter(is_approved=approved.lower() == "true")
        return queryset


class AdminReviewApproveView(APIView):
    """PUT /api/admin/reviews/{id}/approve/ — Approve or reject a review."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response(
                {"error": "Review not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        approve = request.data.get("approve", True)
        if approve:
            review.is_approved = True
            review.save()
            # Recalculate product average rating
            self._update_product_rating(review.product)
            return Response({"message": "Review approved."})
        else:
            review.delete()
            self._update_product_rating(review.product)
            return Response({"message": "Review rejected and deleted."})

    def _update_product_rating(self, product):
        """Recalculate average rating from approved reviews."""
        avg = Review.objects.filter(
            product=product, is_approved=True
        ).aggregate(avg=Avg("rating"))["avg"]
        product.avg_rating = avg or 0
        product.save(update_fields=["avg_rating"])
