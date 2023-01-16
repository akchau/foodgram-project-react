from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import viewsets, status, mixins
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken


from .exceptions import (
    UserNotFound,
    NotFollower,
    AlreadyFollower,
    IncorrectPassword,
)

from .models import Subscribe
from .serializers import (
    RegistrationSerializer,
    UsersSerializer,
    GetTokenSerializer,
    ChangePasswordSerializer,
)
from recipes.serializers import SubscriptionsSerializers


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


class UserViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    @action(
        detail=False,
    )
    def me(self, request):
        username = request.user.username
        user = get_object_or_404(User, username=username)
        serializer = UsersSerializer(
            user,
            context={'request': request}
        )
        return Response(serializer.data, status.HTTP_200_OK)

    @action(
        detail=False,
    )
    def subscriptions(self, request):
        """Подписки пользователя."""
        followings = User.objects.filter(following=request.user)
        page = self.paginate_queryset(followings)
        if page is not None:
            serializer = SubscriptionsSerializers(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionsSerializers(
            followings, many=True, context={'request': request}
        )
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        password = serializer.validated_data['password']
        username = serializer.validated_data['username']
        user = get_object_or_404(User, username=username)
        user.set_password(password)
        user.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)

    def retrieve(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            serializer = UsersSerializer(user, context={'request': request})
        except User.DoesNotExist:
            raise UserNotFound
        return Response(serializer.data, status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action == 'create':
            return RegistrationSerializer
        return UsersSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'create':
            return (AllowAny(),)
        return super().get_permissions()


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
    if user.check_password(password) and user.is_active:
        token = AccessToken.for_user(user)
        return Response({"auth_token": str(token)}, status.HTTP_200_OK)
    else:
        if not user.is_active:
            return Response(
                {"auth_error": 'Выдача токена запрещена'},
                status.HTTP_403_FORBIDDEN
            )
        return Response(
            {"auth_error": 'Неверный пароль'},
            status.HTTP_403_FORBIDDEN
        )


@api_view(['POST'])
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
    raise IncorrectPassword


@api_view(['POST', 'DELETE'])
def subscribe(request, id):
    """Функция подписки на пользователя"""
    try:
        following = User.objects.get(pk=id)
    except User.DoesNotExist:
        raise UserNotFound

    if request.method == "DELETE":
        try:
            obj = Subscribe.objects.get(
                follower=request.user,
                following=following,
            )
            obj.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        except Subscribe.DoesNotExist:
            raise NotFollower

    elif request.method == "POST":
        try:
            Subscribe.objects.create(
                follower=request.user,
                following=following,
            )
            serializer = UsersSerializer(
                following,
                context={'request': request}
            )
            return Response(serializer.data, status.HTTP_201_CREATED)
        except IntegrityError:
            raise AlreadyFollower
