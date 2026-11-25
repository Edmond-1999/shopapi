from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import AddressListCreateView, LoginView, RegisterView


urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("token_refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("address", AddressListCreateView.as_view(), name="address_list_create"),
]
