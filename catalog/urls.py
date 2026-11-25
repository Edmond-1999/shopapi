from django.urls import path
from .views import (
    CartDetailView,
    CategoryDetailView,
    CategoryListView,
    ProductDetailView,
    ProductListView,
)

urlpatterns = [
    path('products', ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>', ProductDetailView.as_view(), name='product_detail'),
    path('categories', CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>', CategoryDetailView.as_view(), name='category_detail'),
    path('carts/<uuid:cart_id>', CartDetailView.as_view(), name='cart_detail'),
]