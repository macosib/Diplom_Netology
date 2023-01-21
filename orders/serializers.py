from django.db.models import Q
from rest_framework import serializers

from orders.models import OrderItem, Order
from shops.models import ProductInfo
from users.models import Contact
from users.serializers import AccountContactSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'quantity', 'product_info')
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True}
        }


class BasketSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemSerializer(many=True, read_only=True)
    total_sum = serializers.IntegerField(read_only=True)
    contact = AccountContactSerializer(read_only=True)
    items = OrderItemSerializer(many=True, write_only=True)
    state = serializers.CharField(required=False)

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'state', 'dt', 'total_sum', 'contact', 'items')
        read_only_fields = ('id',)

    def validate(self, data):
        items = data['items']

        for item in items:
            product_info = item.get('product_info')
            quantity = item.get('quantity')

            product = ProductInfo.objects.filter(id=product_info.id).first()
            if not product:
                raise serializers.ValidationError(
                    {"status": "Failure", "error": "There is no such product"}
                )
            if quantity > product.quantity:
                raise serializers.ValidationError(
                    {"status": "Failure", "error": "There is not enough available product"}
                )
            if quantity <= 0:
                raise serializers.ValidationError(
                    {"status": "Failure", "error": "The quantity of the product must be greater than 0"}
                )
        return data

    def create(self, validated_data):

        user = self.context["request"].user
        items = validated_data.pop('items')

        order, _ = Order.objects.get_or_create(**validated_data, user_id=user.id, state='basket')

        for item in items:
            product_id = item.get('product_info')
            quantity = item.get('quantity', 1)
            OrderItem.objects.update_or_create(
                order=order,
                product_info=product_id,
                defaults={'quantity': quantity}
            )
        return order

    def update(self, instance, validated_data):
        instance.ordered_items.all().delete()
        instance = super().create(**validated_data)
        return instance


class OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(write_only=True)
    contact = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ('id', 'contact')

    def validate(self, data):
        order_id = data.get('id')
        contact_id = data.get('contact')
        user = self.context["request"].user

        contact = Contact.objects.filter(Q(user_id=user.id) & Q(id=contact_id)).first()
        order = Order.objects.filter(Q(id=order_id) & Q(user_id=user.id)).first()

        if not contact:
            raise serializers.ValidationError(
                {"status": "Failure", "error": "To confirm the order, you need to add contacts"}
            )
        if not order:
            raise serializers.ValidationError(
                {"status": "Failure", "error": "The order does not exist"}
            )
        return order
