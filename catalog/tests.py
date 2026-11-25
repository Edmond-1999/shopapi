from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Cart, CartItem, Category, Product, Review
from accounts.models import User


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
                'id': self.active_product.id,
                'title': 'Laptop',
                'price': 999.99,
                'description': 'A laptop',
                'sku': 'LAPTOP-001',
            }],
        )

    def test_category_detail_returns_404_for_unknown_slug(self):
        response = self.client.get(reverse('category_detail', kwargs={'slug': 'unknown'}))

        self.assertEqual(response.status_code, 404)

    def test_product_detail_returns_product_by_id(self):
        response = self.client.get(
            reverse('product_detail', kwargs={'pk': self.active_product.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.active_product.id)
        self.assertEqual(response.json()['sku'], 'LAPTOP-001')

    def test_product_detail_returns_404_for_inactive_product(self):
        inactive_product = Product.objects.get(sku='LAPTOP-OLD')

        response = self.client.get(
            reverse('product_detail', kwargs={'pk': inactive_product.id})
        )

        self.assertEqual(response.status_code, 404)


class CartEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Books', slug='books')
        self.product = Product.objects.create(
            category=self.category,
            title='Django Handbook',
            description='A guide',
            price='25.50',
            sku='DJANGO-001',
            is_active=True,
        )
        self.cart = Cart.objects.create()
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_cart_detail_returns_items_and_total(self):
        response = self.client.get(
            reverse('cart_detail', kwargs={'cart_id': self.cart.cart_id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['cart_id'], str(self.cart.cart_id))
        self.assertEqual(response.json()['items'][0]['line_total'], 51.0)
        self.assertEqual(response.json()['total'], 51.0)

    def test_post_adds_cart_item_and_returns_updated_total(self):
        response = self.client.post(
            reverse('cart_detail', kwargs={'cart_id': self.cart.cart_id}),
            {'product_id': self.product.id, 'quantity': 1},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['items'][0]['quantity'], 3)
        self.assertEqual(response.json()['total'], 76.5)

    def test_cart_browsable_api_renders_add_item_form(self):
        response = self.client.get(
            reverse('cart_detail', kwargs={'cart_id': self.cart.cart_id}),
            HTTP_ACCEPT='text/html',
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="product_id"')
        self.assertContains(response, 'name="quantity"')

    def test_cart_detail_returns_404_for_unknown_cart(self):
        response = self.client.get(
            reverse(
                'cart_detail',
                kwargs={'cart_id': '00000000-0000-0000-0000-000000000000'},
            )
        )

        self.assertEqual(response.status_code, 404)


class ReviewEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Books', slug='books')
        self.product = Product.objects.create(
            category=self.category,
            title='Django Handbook',
            description='A guide',
            price='25.50',
            sku='DJANGO-001',
            is_active=True,
        )
        self.other_product = Product.objects.create(
            category=self.category,
            title='Python Handbook',
            description='Another guide',
            price='30.00',
            sku='PYTHON-001',
            is_active=True,
        )
        self.user = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='test-password',
            phone='1234567890',
        )
        Review.objects.create(
            product=self.product,
            name=self.user,
            rating=5,
            comment='Great book',
        )
        Review.objects.create(
            product=self.other_product,
            name=self.user,
            rating=4,
            comment='Another great book',
        )

    def test_product_reviews_are_scoped_to_the_product(self):
        response = self.client.get(
            reverse(
                'product-reviews-list',
                kwargs={'product_pk': self.product.id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['comment'], 'Great book')
        self.assertEqual(response.json()[0]['name'], self.user.id)

    def test_head_and_options_are_public(self):
        url = f'/api/v1/products/{self.product.id}/reviews'
        for method in ('HEAD', 'OPTIONS'):
            with self.subTest(method=method):
                response = self.client.generic(method, url)
                self.assertEqual(response.status_code, 200)

    def test_product_reviews_endpoint_supports_url_without_trailing_slash(self):
        response = self.client.get(
            f'/api/v1/products/{self.product.id}/reviews'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_authenticated_user_can_create_review_for_product(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/v1/products/{self.product.id}/reviews',
            {'rating': 3, 'comment': 'A useful reference'},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        review = Review.objects.get(comment='A useful reference')
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.name, self.user)

    def test_anonymous_user_cannot_create_review(self):
        response = self.client.post(
            f'/api/v1/products/{self.product.id}/reviews',
            {'rating': 3, 'comment': 'A useful reference'},
            format='json',
        )

        self.assertEqual(response.status_code, 401)

    def test_product_reviews_returns_404_for_unknown_product(self):
        response = self.client.get(
            reverse(
                'product-reviews-list',
                kwargs={'product_pk': 999999},
            )
        )

        self.assertEqual(response.status_code, 404)
