from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"admin/discounts", views.AdminDiscountViewSet, basename="admin-discounts")

urlpatterns = [
    path("discounts/apply/", views.DiscountApplyView.as_view(), name="discount-apply"),
    path("", include(router.urls)),
]
