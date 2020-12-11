from rest_framework import serializers
from .models import Restaurant, Food, Order, Menu


class RestaurantResponseSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    username = serializers.CharField(required=True)
    is_open = serializers.BooleanField(required=True)


class FoodSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        food = Food.objects.create(
            name=validated_data['name'],
            price=validated_data['price'],
            availability=validated_data['availability']
        )
        food.save()
        return food

    class Meta:
        model = Food
        fields = ['id', 'name', 'price', 'availability']


class OrderSerializer(serializers.ModelSerializer):
    foods = FoodSerializer(many=True, read_only=True)
    restaurant = RestaurantResponseSerializer(read_only = True)

    def create(self, validated_data):
        order = Order.objects.create(
            foods=validated_data['foods'],
            status=validated_data['status'],
            restaurant=validated_data['restaurant'],
            customer=validated_data['customer']
        )
        total_price = 0
        for food in order.foods:
            total_price = total_price + food.price
        order.total_price = total_price
        order.save()
        return order

    class Meta:
        model = Order
        fields = ['id', 'foods', 'total_price', 'status', 'restaurant', 'customer']


class MenuSerializer(serializers.HyperlinkedModelSerializer):
    foods = FoodSerializer(many=True, read_only=True)

    def create(self, validated_data):
        menu = Menu.objects.create()
        menu.save()
        return menu

    class Meta:
        model = Menu
        fields = ['foods']


class RestaurantSerializer(serializers.ModelSerializer):
    menu = MenuSerializer(read_only=True)
    orders = OrderSerializer(many=True, read_only=True)

    def create(self, validated_data):
        restaurant = Restaurant.objects.create(
            username=validated_data['username']
        )
        restaurant.save()
        return restaurant

    class Meta:
        model = Restaurant
        fields = ['username', 'is_open', 'menu']
