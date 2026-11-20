from django.urls import path
from .views import CategoryDetailView, CategoryListView, ProductListView

urlpatterns = [
    path('products', ProductListView.as_view(), name='product_list'),
    path('categories', CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>', CategoryDetailView.as_view(), name='category_detail'),
]