from django.urls import path

from orders.views import BasketView, OrderView, PartnerOrders

urlpatterns = [
    path("basket", BasketView.as_view(), name="basket"),
    path("order", OrderView.as_view(), name="order"),
    path("partner/orders", PartnerOrders.as_view(), name="partner-orders"),
]
