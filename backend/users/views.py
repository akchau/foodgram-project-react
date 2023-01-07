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
    ChangePasswordSerializer,
    CurrentUserSerializer
)

User = get_user_model()


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def users_view(request):
    """
    POST - регистрация пользователей
    GET - получение списка прользователей
    """
    if request.method == "POST":
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        password = serializer.validated_data['password']
        username = serializer.validated_data['username']
        user = get_object_or_404(User, username=username)
        user.set_password(password)
        user.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    users = User.objects.all()
    serializer = UsersSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_view(request):
    """
    Получение токена авторизации.
    """
    user_serializer = GetTokenSerializer(data=request.data)
    user_serializer.is_valid(raise_exception=True)
    email = user_serializer.validated_data['email']
    password = user_serializer.validated_data['password']
    user = get_object_or_404(User, email=email)
    if user.check_password(password):
        token = AccessToken.for_user(user)
        return Response({"auth_token": str(token)}, status.HTTP_200_OK)
    else:
        return Response(
            {"auth_error": 'Неверный пароль'},
            status.HTTP_403_FORBIDDEN
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def set_password(request):
    """
    Функция изменения пароля
    """
    password_serializer = ChangePasswordSerializer(data=request.data)
    password_serializer.is_valid(raise_exception=True)
    new_password = password_serializer.validated_data['new_password']
    current_password = password_serializer.validated_data['current_password']
    user = request.user
    if user.check_password(current_password):
        user.set_password(new_password)
        user.save()
        return Response(password_serializer.data, status.HTTP_204_NO_CONTENT)
    return Response(
            {"detail": "Учетные данные не были предоставлены."},
            status.HTTP_401_UNAUTHORIZED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def current_user(request):
    serializer = CurrentUserSerializer(request.user)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    serializer = CurrentUserSerializer(user)
    return Response(serializer.data, status.HTTP_200_OK)
