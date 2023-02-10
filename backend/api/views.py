from django.db.models import Sum, Q
from django.db.utils import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from urllib.parse import unquote


from .exceptions import (
    UserNotFound,
    NotFollower,
    AlreadyFollower,
    AlreadyInCart
)
from .serializers import (
    UsersSerializer,
    SubscriptionsSerializers,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeWriteSerializer,
    CompactRecipeSerializer,
    UserWithRecipesSerializer
)
from .paginators import PagePagination
from .permissions import AdminOrReadOnly, RecipePermissions, UserPermission
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


class UserViewSet(DjoserUserViewSet):
    """
    Вьюсет для модели пользователя
    """
    serializer_class = UsersSerializer
    permission_classes = (UserPermission,)
    pagination_class = PagePagination

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """
        Функция для получения подписок
        авторизованного пользователя
        """
        following = User.objects.filter(follower__follower=request.user)
        page = self.paginate_queryset(following)
        if page is not None:
            serializer = SubscriptionsSerializers(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionsSerializers(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
    )
    def me(self, request):
        """
        Функция для собственного профиля авторизованного пользователя
        """
        username = request.user.username
        user = get_object_or_404(User, username=username)
        serializer = UsersSerializer(
            user,
            context={'request': request}
        )
        return Response(serializer.data, status.HTTP_200_OK)

    @action(
        methods=['post', 'delete'],
        detail=True,
    )
    def subscribe(self, request, id):
        """
        Функция для подписки и отписки от пользователя
        """
        # проверка существования пользовтеля
        try:
            following = User.objects.get(pk=id)
        except User.DoesNotExist:
            raise UserNotFound
        # отписка
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
        # подписка
        elif request.method == "POST":
            try:
                Subscribe.objects.create(
                    follower=request.user,
                    following=following,
                )
                serializer = UserWithRecipesSerializer(
                    following,
                    context={'request': request}
                )
                return Response(serializer.data, status.HTTP_201_CREATED)
            except IntegrityError:
                raise AlreadyFollower

    def create(self, request):
        """
        Регистрация пользователя
        """
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
        """
        Получение списка всех пользователей
        """
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

    def retrieve(self, request, id):
        """
        Получение данных пользователя
        """
        try:
            user = User.objects.get(pk=id)
            serializer = UsersSerializer(user, context={'request': request})
        except User.DoesNotExist:
            raise UserNotFound
        return Response(serializer.data, status.HTTP_200_OK)


DATE_FORMAT = '%d-%m-%Y %H:%M'


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет рецепта
    """
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags__slug', 'author')
    permission_classes = (RecipePermissions,)
    pagination_class = PagePagination

    def get_queryset(self):
        """
        Выбор списка рецептов в зависимости от страницы
        """
        # корзнина покупок
        if self.request.query_params.get('is_in_shopping_cart') == '1':
            if self.request.user.is_authenticated:
                queryset = Recipe.objects.filter(
                    users_shopping__user=self.request.user
                )
                return queryset
            raise AuthenticationFailed(
                detail="Доступно только авторизованным пользователем")
        # избранное
        elif self.request.query_params.get('is_favorited') == '1':
            if self.request.user.is_authenticated:
                queryset = Recipe.objects.filter(
                    users_favorite__user=self.request.user
                )
                return queryset
            raise AuthenticationFailed(
                detail="Доступно только авторизованным пользователем")
        else:
            # фильтр по связанным тегам
            tags = self.request.query_params.getlist('tags')
            if tags:
                queryset = Recipe.objects.filter(
                    tags__slug__in=tags).distinct()
                return queryset
            # все рецепты
            return Recipe.objects.all()

    def get_serializer_class(self):
        """
        Выбор сериализатора для записи и чтения
        """
        if self.request.method not in SAFE_METHODS:
            return RecipeWriteSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        """
        Автоатическое добавление автора рецепта
        """
        serializer.save(author=self.request.user)

    def destroy(self, request, pk):
        """
        Удаление рецепта
        """
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """
        Добавление и удаление из корзины пользователя
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        # удалить из корзины
        if request.method == "DELETE":
            get_object_or_404(
                UserShoppingCartRecipes,
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status.HTTP_204_NO_CONTENT)
        # добавить в корзину
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
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """
        Добавление и удаление из избранного
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        # удаление из избранного
        if request.method == "DELETE":
            try:
                get_object_or_404(
                    UserFavoriteRecipes,
                    user=request.user,
                    recipe=recipe
                ).delete()
            except UserFavoriteRecipes.DoesNotExist:
                return Response({"errors": "Не в избранном."})
            return Response(status.HTTP_204_NO_CONTENT)
        # добавление в избранное
        elif request.method == "POST":
            if UserFavoriteRecipes.objects.filter(
                    user=request.user,
                    recipe=Recipe.objects.get(pk=pk)
            ).exists():
                return Response({"errors": "Уже в избранном."})
            UserFavoriteRecipes.objects.create(
                user=request.user,
                recipe=Recipe.objects.get(pk=pk)
            )
            serializer = CompactRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status.HTTP_201_CREATED)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """
        Скачивание корзины
        """
        recipes = Recipe.objects.filter(users_shopping__user=request.user)
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
    permission_classes = (AdminOrReadOnly,)

    def get_queryset(self):
        """
        Поиск по ингридиентам для воода в форму создания
        """
        name = self.request.query_params.get('name')
        queryset = self.queryset
        if name:
            if name[0] == '%':
                name = unquote(name)
            name = name.lower()
            stw_queryset = queryset.filter(
                Q(name__startswith=name) & Q(name__contains=name))
            return stw_queryset
        return queryset


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для тегов
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
