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
    AlreadyFavorite,
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
from .permissions import AuthorOrReadOnly, AdminOrReadOnly, RecipePermissions, UserPermission
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
    serializer_class = UsersSerializer
    permission_classes = (UserPermission,)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Подписки пользователя."""
        subscribes = Subscribe
        page = self.paginate_queryset(following)
        if page is not None:
            serializer = SubscriptionsSerializers(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionsSerializers(
            following, many=True, context={'request': request}
        )
        return Response(serializer.data)

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
        methods=['post', 'delete'],
        detail=True,
    )
    def subscribe(self, request, id):
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
                serializer = UserWithRecipesSerializer(
                    following,
                    context={'request': request}
                )
                return Response(serializer.data, status.HTTP_201_CREATED)
            except IntegrityError:
                raise AlreadyFollower

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

    def retrieve(self, request, id):
        try:
            user = User.objects.get(pk=id)
            serializer = UsersSerializer(user, context={'request': request})
        except User.DoesNotExist:
            raise UserNotFound
        return Response(serializer.data, status.HTTP_200_OK)


DATE_FORMAT = '%d-%m-%Y %H:%M'


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags__slug', 'author')
    permission_classes = (RecipePermissions,)

    def get_queryset(self):
        if self.request.query_params.get('is_in_shopping_cart') == '1':
            if self.request.user.is_authenticated:
                queryset = Recipe.objects.filter(
                    users_shopping__user=self.request.user
                )
                return queryset
            raise AuthenticationFailed(
                detail="Доступно только авторизованным пользователем")
        elif self.request.query_params.get('is_favorited') == '1':
            if self.request.user.is_authenticated:
                queryset = Recipe.objects.filter(
                    users_favorite__user=self.request.user
                )
                return queryset
            raise AuthenticationFailed(
                detail="Доступно только авторизованным пользователем")
        else:
            return Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method not in SAFE_METHODS:
            return RecipeWriteSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, pk):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
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
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "DELETE":
            try:
                get_object_or_404(
                    UserFavoriteRecipes,
                    user=request.user,
                    recipe=recipe
                ).delete()
            except:
                return Response({"errors": "Не в избранном."})
            return Response(status.HTTP_204_NO_CONTENT)

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


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        """Получает queryset в соответствии с параметрами запроса."""
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
