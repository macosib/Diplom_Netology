from django.urls import path

from shops.views import PartnerUpdate, PartnerState, CategoryView, ShopView, ProductView

urlpatterns = [
    path("partner/update", PartnerUpdate.as_view(), name="partner-update"),
    path("partner/state/<int:pk>", PartnerState.as_view(), name="partner-state"),
    path("categories", CategoryView.as_view(), name="categories"),
    path("shops", ShopView.as_view(), name="shops"),
    path("products", ProductView.as_view(), name="products"),
]
