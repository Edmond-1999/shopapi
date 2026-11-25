from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import F
from rest_framework import status, viewsets
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    CartItemAddSerializer,
    CartSerializer,
    CategorySerializer,
    ProductSerializer,
)
from .models import Cart, CartItem, Category, Product, Review


# Create your views here.




# @api_view(['GET'])
# def product_list(request):
#     products = Product.objects.all()
#     products = products.filter(is_active=True)
#     serializer = ProductSerializer(products, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)


class ProductListView(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all().filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class CategoryDetailView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Product.objects.filter(category=category, is_active=True)


class CartDetailView(RetrieveAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    lookup_field = "cart_id"
    lookup_url_kwarg = "cart_id"
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CartItemAddSerializer
        return CartSerializer

    def post(self, request, cart_id):
        cart = get_object_or_404(self.get_queryset(), cart_id=cart_id)
        self.check_object_permissions(request, cart)
        item_serializer = self.get_serializer(data=request.data)
        item_serializer.is_valid(raise_exception=True)
        product = item_serializer.validated_data["product"]
        quantity = item_serializer.validated_data["quantity"]

        with transaction.atomic():
            Cart.objects.select_for_update().get(cart_id=cart.cart_id)
            item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={"quantity": quantity},
            )
            if not created:
                CartItem.objects.filter(pk=item.pk).update(
                    quantity=F("quantity") + quantity
                )

        cart.refresh_from_db()
        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK,
        )


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer.ProductReviewSerializer

    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        return {'user': self.request.user, 'product': self.kwargs['product_pk']}

    def get_product(self):
        return get_object_or_404(
            Product,
            pk=self.kwargs['product_pk'],
            is_active=True,
        )

    def get_queryset(self):
        return Review.objects.filter(product=self.get_product())

    def perform_create(self, serializer):
        serializer.save(product=self.get_product(), name=self.request.user)