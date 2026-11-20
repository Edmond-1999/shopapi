from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Category, Product


class CategoryEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.active_product = Product.objects.create(
            category=self.category,
            title='Laptop',
            description='A laptop',
            price='999.99',
            sku='LAPTOP-001',
            is_active=True,
        )
        Product.objects.create(
            category=self.category,
            title='Old laptop',
            price='499.99',
            sku='LAPTOP-OLD',
            is_active=False,
        )

    def test_category_list(self):
        response = self.client.get(reverse('category_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{'name': 'Electronics', 'slug': 'electronics'}])

    def test_category_detail_returns_active_products_by_slug(self):
        response = self.client.get(reverse('category_detail', kwargs={'slug': 'electronics'}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [{
                'title': 'Laptop',
                'price': 999.99,
                'description': 'A laptop',
                'sku': 'LAPTOP-001',
            }],
        )

    def test_category_detail_returns_404_for_unknown_slug(self):
        response = self.client.get(reverse('category_detail', kwargs={'slug': 'unknown'}))

        self.assertEqual(response.status_code, 404)
