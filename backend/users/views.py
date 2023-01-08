from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken


from .models import Subscribe
from .serializers import (
    RegistrationSerializer,
    UsersSerializer,
    GetTokenSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


def get_response(key):
    """Функция получает на вход ключ ошибки

    Args:
        key (str): Ключ ошибки:
        - "not_found": Объект не найден
        - "not_authenticated": Пользователь не авторизован
        - "not_follower": Не подписан на объект, от которого отписывается
        - "already_follower": Подписан на объект, на который подписывается

    Returns:
        _type_: _description_
    """
    keys = {
        "not_found": {"detail": "Страница не найдена."},
        "not_authenticated":
            {"detail": "Учетные данные не были предоставлены."},
        "not_follower": {"errors": "Вы не подписаны"},
        "already_follower": {"errors": "Вы уже подписаны"},
    }
    return JSONRenderer().render(keys[key])


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
    serializer = UsersSerializer(
        users,
        many=True,
        context={'request': request}
    )
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
    serializer = UsersSerializer(request.user, context={'request': request})
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def profile(request, id):
    user = get_object_or_404(User, pk=id)
    serializer = UsersSerializer(user, context={'request': request})
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes([AllowAny])
def subscribe(request, id):
    """Функция подписки на пользователя"""

    try:
        following = User.objects.get(pk=id)
    except User.DoesNotExist:
        return Response(get_response("not_found"), status.HTTP_404_NOT_FOUND)

    if not request.user.is_authenticated:
        return Response(
            get_response("not_authenticated"),
            status.HTTP_401_UNAUTHORIZED
        )
    follower = request.user

    if request.method == "DELETE":
        try:
            obj = Subscribe.objects.get(
                follower=follower,
                following=following,
            )
            obj.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        except Subscribe.DoesNotExist:
            return Response(
                get_response("not_follower"),
                status.HTTP_400_BAD_REQUEST
            )

    elif request.method == "POST":
        try:
            Subscribe.objects.create(
                follower=follower,
                following=following,
            )
            serializer = UsersSerializer(
                following,
                context={'request': request}
            )
            return Response(serializer.data, status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                get_response("already_follower"),
                status.HTTP_400_BAD_REQUEST
            )


@api_view(['GET'])
@permission_classes([AllowAny])
def my_subscriptions(request):
    """Подписки пользователя."""
    if not request.user.is_authenticated:
        return Response(
            get_response("not_authenticated"),
            status.HTTP_401_UNAUTHORIZED
        )
    followings = User.objects.filter(follower__follower=request.user)
    serializer = UsersSerializer(
        followings,
        many=True,
        context={'request': request}
    )
    return Response(serializer.data, status.HTTP_200_OK)
