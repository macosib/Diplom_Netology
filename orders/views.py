from rest_framework import status

from orders.models import Order, OrderItem
from orders.serializers import OrderItemSerializer, BasketSerializer
from orders.signals import new_order
from django.db import IntegrityError
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ujson import loads as load_json


class BasketView(APIView):
    """
    Класс для работы с корзиной пользователя

    """

    permission_classes = [IsAuthenticated]
    queryset = Order.objects.filter(state=True)
    serializer_class = BasketSerializer

    def put(self, request, *args, **kwargs):
        serializer = BasketSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"status": "Success", "message": "Items in the shopping cart have been changed"},
                status=status.HTTP_200_OK)

    # # редактировать корзину
    def post(self, request, *args, **kwargs):
        serializer = BasketSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"status": "Success", "message": "Products added"}, status=status.HTTP_200_OK)

    def delete(self, request):
        order = Order.objects.filter(user=request.user, state='basket').first()

        if not order:
            return Response({"status": "Failure", "error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        order.delete()
        return Response({"status": "Success", "message": "The basket is cleared"}, status=status.HTTP_204_NO_CONTENT)



#
# class PartnerOrders(APIView):
#     """
#     Класс для получения заказов поставщиками
#     """
#
#     def get(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
#
#         if request.user.type != 'shop':
#             return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)
#
#         order = Order.objects.filter(
#             ordered_items__product_info__shop__user_id=request.user.id).exclude(state='basket').prefetch_related(
#             'ordered_items__product_info__product__category',
#             'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
#             total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
#
#         serializer = BasketSerializer(order, many=True)
#         return Response(serializer.data)
#
#
# class OrderView(APIView):
#     """
#     Класс для получения и размешения заказов пользователями
#     """
#
#     # получить мои заказы
#     def get(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
#         order = Order.objects.filter(
#             user_id=request.user.id).exclude(state='basket').prefetch_related(
#             'ordered_items__product_info__product__category',
#             'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
#             total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
#
#         serializer = BasketSerializer(order, many=True)
#         return Response(serializer.data)
#
#     # разместить заказ из корзины
#     def post(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
#
#         if {'id', 'contact'}.issubset(request.data):
#             if request.data['id'].isdigit():
#                 try:
#                     is_updated = Order.objects.filter(
#                         user_id=request.user.id, id=request.data['id']).update(
#                         contact_id=request.data['contact'],
#                         state='new')
#                 except IntegrityError as error:
#                     print(error)
#                     return JsonResponse({'Status': False, 'Errors': 'Неправильно указаны аргументы'})
#                 else:
#                     if is_updated:
#                         new_order.send(sender=self.__class__, user_id=request.user.id)
#                         return JsonResponse({'Status': True})
#
#         return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
