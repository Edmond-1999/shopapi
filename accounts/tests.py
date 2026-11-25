from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


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
