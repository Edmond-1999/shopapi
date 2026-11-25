from rest_framework import serializers
from .models import Cart, CartItem, Product, Category

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'description', 'sku']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug']


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.title", read_only=True)
    line_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "line_total"]


class CartItemAddSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        source="product",
        queryset=Product.objects.filter(is_active=True),
    )
    quantity = serializers.IntegerField(min_value=1)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["cart_id", "items", "total"]

    def get_total(self, cart):
        return sum(
            (item.line_total for item in cart.items.all()),
            start=0,
        )