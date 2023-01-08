from django.urls import path

from orders.views import BasketView, OrderView

urlpatterns = [
    path('basket', BasketView.as_view(), name='basket'),
    path('order', OrderView.as_view(), name='order'),
]