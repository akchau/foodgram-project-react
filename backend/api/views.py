from django.db.models import Sum
from django.db.utils import IntegrityError

from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
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
    AlreadyFavorite,
    NotRules,
    AlreadyInCart
)
from .serializers import (
    RegistrationSerializer,
    UsersSerializer,
    GetTokenSerializer,
    ChangePasswordSerializer,
    SubscriptionsSerializers,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeWriteSerializer,
)
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    UserFavoriteRecipes,
    UserShoppingCartRecipes,

)

from users.models import Subscribe, User


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


DATE_FORMAT = '%d-%m-%Y %H:%M'


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags__slug', 'author')

    def get_queryset(self):
        if self.request.query_params.get('is_in_shopping_cart') == '1':
            return Recipe.objects.filter(
                users_shopping__user=self.request.user
            )
        if self.request.query_params.get('is_favorited') == '1':
            return Recipe.objects.filter(
                users_favorite__user=self.request.user
            )
        return Recipe.objects.all()

    def get_serializer_class(self):
        if (
            self.action == 'create'
            or self.action == 'partial_update'
            or self.action == 'update'
        ):
            return RecipeWriteSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, pk):
        instance = self.get_object()
        if request.user != instance.author:
            raise NotRules
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == "DELETE":
            get_object_or_404(
                UserShoppingCartRecipes,
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status.HTTP_204_NO_CONTENT)

        elif request.method == "POST":
            if UserShoppingCartRecipes.objects.filter(
                    user=request.user,
                    recipe=Recipe.objects.get(pk=pk)
            ).exists():
                raise AlreadyInCart
            UserShoppingCartRecipes.objects.create(
                user=request.user,
                recipe=Recipe.objects.get(pk=pk)
            )
            serializer = RecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['post', 'delete'],
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "DELETE":
            get_object_or_404(
                UserFavoriteRecipes,
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status.HTTP_204_NO_CONTENT)

        elif request.method == "POST":
            if UserFavoriteRecipes.objects.filter(
                    user=request.user,
                    recipe=Recipe.objects.get(pk=pk)
            ).exists():
                raise AlreadyFavorite
            UserFavoriteRecipes.objects.create(
                user=request.user,
                recipe=Recipe.objects.get(pk=pk)
            )
            serializer = RecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status.HTTP_201_CREATED)

    @action(
        detail=False,
    )
    def download_shopping_cart(self, request):
        recipes = Recipe.objects.filter(users_shopping__user=request.user)
        print(recipes)
        ingredients = Ingredient.objects.filter(
            recipe__in=recipes).annotate(
                sum_amount=Sum('ingredientrecipe__amount')
        )
        user = request.user
        filename = f'{user.username}_buy_list.txt'
        shopping_list = (
            f'Список покупок для:\n\n{user.first_name} {user.last_name}\n'
            f'{timezone.now().strftime(DATE_FORMAT)}\n'
        )
        for ing in ingredients:
            shopping_list += (
                f'{ing.name}: {ing.sum_amount} {ing.measurement_unit}\n'
            )

        shopping_list += '\nСоздано Foodgram'

        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
