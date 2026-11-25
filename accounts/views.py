from django.db import transaction
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Address
from .serializers import AddressSerializer, LoginSerializer, RegisterSerializer


class AddressListCreateView(ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        user = User.objects.select_for_update().get(
            pk=self.request.user.pk
        )

        if serializer.validated_data.get("is_default", False):
            Address.objects.filter(
                user=user,
                is_default=True
            ).update(is_default=False)

        serializer.save(user=user)


class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
