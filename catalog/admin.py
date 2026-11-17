from django.contrib import admin

from catalog.models import Product, Category


# Register your models here.



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name',]
    list_filter = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category','price', 'sku', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'sku', 'description']
    list_editable = ['price', 'is_active']

