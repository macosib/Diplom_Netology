import yaml
from django.db.models import Q
from requests import get
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from yaml import SafeLoader

from shops.models import Shop, Category, ProductInfo, Product, Parameter, ProductParameter
from shops.permissions import IsShop
from shops.serializers import PartnerUpdateSerializer, CategorySerializer, ShopSerializer, ProductInfoSerializer
from users.permisssions import IsOwner


import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class PartnerUpdate(APIView):
    permission_classes = [IsAuthenticated, IsShop]
    serializer_class = PartnerUpdateSerializer
    """
    Класс для обновления прайса от поставщика
    """

    def post(self, request, *args, **kwargs):
        serializer = PartnerUpdateSerializer(data=request.data)
        print(serializer.is_valid())
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        url = serializer.validated_data.get('url')
        print(url)

        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        stream = session.get(url)

        #
        # # stream = get(url).content
        # data = yaml.load(stream, Loader=SafeLoader)
        try:
            stream = get(url).content
            data = yaml.load(stream, Loader=SafeLoader)
        except Exception as error:
            return Response({"status": "Failure", "error": "Failed to read file"}, status=status.HTTP_400_BAD_REQUEST)

        print(data)
        shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)

        for category in data['categories']:
            category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
            category_object.shops.add(shop.id)
            category_object.save()

        ProductInfo.objects.filter(shop_id=shop.id).delete()

        for item in data['goods']:
            product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])
            product_info = ProductInfo.objects.create(product_id=product.id,
                                                      external_id=item['id'],
                                                      model=item['model'],
                                                      price=item['price'],
                                                      price_rrc=item['price_rrc'],
                                                      quantity=item['quantity'],
                                                      shop_id=shop.id)
            for name, value in item['parameters'].items():
                parameter_object, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(product_info_id=product_info.id,
                                                parameter_id=parameter_object.id,
                                                value=value)
        return Response({
            "status": "Success",
            'message': "Data uploaded successfully"
        }, status=status.HTTP_200_OK)


class CategoryView(ListAPIView):
    """
    Класс для просмотра категорий
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class ShopView(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """

    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]


class ProductView(APIView):
    """
    Класс для поиска товаров
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProductInfoSerializer

    def get(self, request, *args, **kwargs):

        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        queryset = ProductInfo.objects.filter(
            query).select_related(
            'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()

        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)


class PartnerState(RetrieveUpdateAPIView):
    """
    Класс для работы со статусом поставщика
    """
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated, IsShop, IsOwner]
