from django.db.models import Sum, F
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from orders.serializers import BasketSerializer, OrderSerializer
from orders.tasks import new_order
from shops.permissions import IsShop


class BasketView(APIView):
    """
    Класс для работы с корзиной пользователя

    """

    permission_classes = [IsAuthenticated]
    queryset = Order.objects.filter(state=True)
    serializer_class = BasketSerializer

    def get(self, request):
        basket = (
            Order.objects.filter(user=self.request.user, state="basket")
            .prefetch_related("ordered_items")
            .annotate(
                total_price=Sum(
                    F("ordered_items__quantity")
                    * F("ordered_items__product_info__price")
                )
            )
            .first()
        )
        serializer = BasketSerializer(basket)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer = BasketSerializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "status": "Success",
                    "message": "Items in the shopping cart have been changed",
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        serializer = BasketSerializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"status": "Success", "message": "Products added"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        order = Order.objects.filter(user=request.user, state="basket").first()
        if not order:
            return Response(
                {"status": "Failure", "error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        order.delete()
        return Response(
            {"status": "Success", "message": "The basket is cleared"},
            status=status.HTTP_204_NO_CONTENT,
        )


class PartnerOrders(APIView):
    """
    Класс для получения заказов поставщиками
    """

    permission_classes = [IsAuthenticated, IsShop]
    serializer_class = BasketSerializer

    def get(self, request, *args, **kwargs):
        order = (
            Order.objects.filter(
                ordered_items__product_info__shop__user_id=request.user.id
            )
            .exclude(state="basket")
            .prefetch_related(
                "ordered_items__product_info__product__category",
                "ordered_items__product_info__product_parameters__parameter",
            )
            .select_related("contact")
            .annotate(
                total_sum=Sum(
                    F("ordered_items__quantity")
                    * F("ordered_items__product_info__price")
                )
            )
            .distinct()
        )
        serializer = BasketSerializer(order, many=True)
        return Response(serializer.data)


class OrderView(APIView):
    """
    Класс для получения и размешения заказов пользователями
    """

    permission_classes = [IsAuthenticated]
    serializer_class = BasketSerializer

    def get(self, request, *args, **kwargs):
        order = (
            Order.objects.filter(user_id=request.user.id)
            .exclude(state="basket")
            .prefetch_related(
                "ordered_items__product_info__product__category",
                "ordered_items__product_info__product_parameters__parameter",
            )
            .select_related("contact")
            .annotate(
                total_sum=Sum(
                    F("ordered_items__quantity")
                    * F("ordered_items__product_info__price")
                )
            )
            .distinct()
        )
        serializer = BasketSerializer(order, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            order = serializer.validated_data
            order.state = "new"
            order.save()
            new_order.delay(order, request.user)
            return Response(
                {"status": "Success", "message": "Products added"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
