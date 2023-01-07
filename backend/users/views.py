from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken

from .serializers import (
    RegistrationSerializer,
    UsersSerializer,
    GetTokenSerializer,

)
User = get_user_model()


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def users_view(request):
    """
    Функция создает пользователя и
    отправляет ему на почту код подтверждения.
    """
    if request.method == "POST":
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    users = User.objects.all()
    serializer = UsersSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_view(request):
    user_serializer = GetTokenSerializer(data=request.data)
    user_serializer.is_valid(raise_exception=True)
    email = user_serializer.validated_data['email']
    password = user_serializer.validated_data['password']

    user = get_object_or_404(User, email=email)
    if user.password == password:
        token = AccessToken.for_user(user)
        return Response({"auth_token": str(token)}, status.HTTP_200_OK)
    else:
        return Response({"auth_error": 'Неверный пароль'}, status.HTTP_403_FORBIDDEN)
