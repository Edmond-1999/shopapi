from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Address


class AuthenticationEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_creates_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "phone": "123456789",
                "password": "strong-password",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], "newuser@example.com")
        self.assertTrue(
            get_user_model().objects.filter(email="newuser@example.com").exists()
        )

    def test_register_browsable_api_renders_form(self):
        response = self.client.get(
            reverse("register"),
            HTTP_ACCEPT="text/html",
        )

        self.assertEqual(response.status_code, 405)
        self.assertContains(response, 'name="email"', status_code=405)
        self.assertContains(response, 'name="password"', status_code=405)

    def test_login_returns_jwt_tokens(self):
        get_user_model().objects.create_user(
            username="loginuser",
            email="login@example.com",
            phone="123456789",
            password="strong-password",
        )

        response = self.client.post(
            reverse("login"),
            {"email": "login@example.com", "password": "strong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_token_refresh_returns_new_access_token(self):
        get_user_model().objects.create_user(
            username="refreshuser",
            email="refresh@example.com",
            phone="123456789",
            password="strong-password",
        )
        login_response = self.client.post(
            reverse("login"),
            {"email": "refresh@example.com", "password": "strong-password"},
            format="json",
        )

        response = self.client.post(
            reverse("token_refresh"),
            {"refresh": login_response.json()["refresh"]},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())


class AddressEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="addressuser",
            email="address@example.com",
            phone="123456789",
            password="strong-password",
        )
        self.other_user = get_user_model().objects.create_user(
            username="otheruser",
            email="other@example.com",
            phone="987654321",
            password="strong-password",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_address_uses_authenticated_user(self):
        response = self.client.post(
            reverse("address_list_create"),
            {
                "label": "home",
                "recipient_name": "Address User",
                "phone": "123456789",
                "line1": "1 Main Street",
                "city": "Lagos",
                "state": "Lagos",
                "country": "Nigeria",
                "is_default": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        address = Address.objects.get(id=response.json()["id"])
        self.assertEqual(address.user, self.user)
        self.assertTrue(address.is_default)

    def test_list_returns_only_authenticated_users_addresses(self):
        own_address = Address.objects.create(
            user=self.user,
            recipient_name="Address User",
            phone="123456789",
            line1="1 Main Street",
            city="Lagos",
            state="Lagos",
        )
        Address.objects.create(
            user=self.other_user,
            recipient_name="Other User",
            phone="987654321",
            line1="2 Other Street",
            city="Abuja",
            state="FCT",
        )

        response = self.client.get(reverse("address_list_create"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.json()], [own_address.id])

    def test_making_new_default_address_replaces_existing_default(self):
        Address.objects.create(
            user=self.user,
            recipient_name="Old Address",
            phone="123456789",
            line1="1 Main Street",
            city="Lagos",
            state="Lagos",
            is_default=True,
        )

        response = self.client.post(
            reverse("address_list_create"),
            {
                "recipient_name": "New Address",
                "phone": "123456789",
                "line1": "2 Main Street",
                "city": "Lagos",
                "state": "Lagos",
                "is_default": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            Address.objects.filter(user=self.user, is_default=True).count(),
            1,
        )
