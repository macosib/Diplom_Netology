import yaml
from django_filters.rest_framework import DjangoFilterBackend
from requests import get
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from yaml import SafeLoader

from shops.filters import ProductInfoFilter
from shops.models import (
    Shop,
    Category,
    ProductInfo,
    Product,
    Parameter,
    ProductParameter,
)
from shops.permissions import IsShop
from shops.serializers import (
    PartnerUpdateSerializer,
    CategorySerializer,
    ShopSerializer,
    ProductInfoSerializer,
)
from users.permisssions import IsOwner


class PartnerUpdate(APIView):
    permission_classes = [IsAuthenticated, IsShop]
    serializer_class = PartnerUpdateSerializer
    """
    Класс для обновления прайса от поставщика
    """

    def post(self, request, *args, **kwargs):
        serializer = PartnerUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        url = serializer.validated_data.get("url")
        try:
            stream = get(url).content
            data = yaml.load(stream, Loader=SafeLoader)
            # with open("./data/upload.yaml", "r") as stream:
            #     try:
            #         data = yaml.safe_load(stream)
            #     except yaml.YAMLError as exc:
            #         print(exc)
        except Exception as error:
            print(error)
            return Response(
                {"status": "Failure", "error": "Failed to read file"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        shop, _ = Shop.objects.get_or_create(name=data["shop"], user_id=request.user.id)

        for category in data["categories"]:
            category_object, _ = Category.objects.get_or_create(
                id=category["id"], name=category["name"]
            )
            category_object.shops.add(shop.id)
            category_object.save()

        ProductInfo.objects.filter(shop_id=shop.id).delete()

        for item in data["goods"]:
            product, _ = Product.objects.get_or_create(
                name=item["name"], category_id=item["category"]
            )
            product_info = ProductInfo.objects.create(
                product_id=product.id,
                external_id=item["id"],
                model=item["model"],
                price=item["price"],
                price_rrc=item["price_rrc"],
                quantity=item["quantity"],
                shop_id=shop.id,
            )
            for name, value in item["parameters"].items():
                parameter_object, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(
                    product_info_id=product_info.id,
                    parameter_id=parameter_object.id,
                    value=value,
                )
        return Response(
            {"status": "Success", "message": "Data uploaded successfully"},
            status=status.HTTP_200_OK,
        )


class PartnerState(RetrieveUpdateAPIView):
    """
    Класс для работы со статусом поставщика
    """

    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated, IsShop, IsOwner]


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


class ProductView(ListAPIView):
    """
    Класс для поиска товаров
    """

    queryset = (
        ProductInfo.objects.select_related("shop", "product__category")
        .prefetch_related("product_parameters__parameter")
        .distinct()
    )
    permission_classes = [IsAuthenticated]
    serializer_class = ProductInfoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductInfoFilter
