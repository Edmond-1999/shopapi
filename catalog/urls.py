from django.urls import path, include
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter

from .views import (
    CartDetailView,
    CategoryDetailView,
    CategoryListView,
    ProductDetailView,
    ProductListView, ReviewViewSet,
)

router = routers.DefaultRouter()

router.register('products', ProductListView, basename='products')

product_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
product_router.register('reviews', ReviewViewSet, basename='product-reviews')



urlpatterns = [
    path('products', ProductListView.as_view({'get': 'list'}), name='product_list'),
    path('products/', ProductListView.as_view({'get': 'list'}), name='product_list'),
    path('products/<int:pk>', ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('categories', CategoryListView.as_view(), name='category_list'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('carts/<uuid:cart_id>', CartDetailView.as_view(), name='cart_detail'),
    path('carts/<uuid:cart_id>/', CartDetailView.as_view(), name='cart_detail'),

    path(
        'products/<int:product_pk>/reviews',
        ReviewViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='product-reviews-list-no-slash',
    ),
    path('', include(router.urls)),
    path('', include(product_router.urls)),

    path('categories/<slug:slug>', CategoryDetailView.as_view(), name='category_detail'),


]
