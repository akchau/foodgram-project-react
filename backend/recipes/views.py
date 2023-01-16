from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db.utils import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from django.http.response import HttpResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .exceptions import NotFavorite, AlreadyFavorite, NotRules, NotInCart
from .models import (
    Tag,
    Ingredient,
    Recipe,
    UserFavoriteRecipes,
    UserShoppingCartRecipes
)
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeWriteSerializer
)

User = get_user_model()

DATE_FORMAT = '%d-%m-%Y %H:%M'


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags__slug', 'author')

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
        recipe = Recipe.objects.get(pk=pk)
        if request.method == "DELETE":
            try:
                obj = UserShoppingCartRecipes.objects.filter(
                    user=request.user,
                    recipe=recipe,
                )
                obj.delete()
                return Response(status.HTTP_204_NO_CONTENT)
            except UserShoppingCartRecipes.DoesNotExist:
                raise NotInCart

        elif request.method == "POST":
            UserShoppingCartRecipes.objects.create(
                user=request.user,
                recipe=Recipe.objects.get(pk=pk),
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
        recipe = Recipe.objects.get(pk=pk)
        if request.method == "DELETE":
            try:
                obj = UserFavoriteRecipes.objects.get(
                    user=request.user,
                    recipe=recipe,
                )
                obj.delete()
                return Response(status.HTTP_204_NO_CONTENT)
            except UserFavoriteRecipes.DoesNotExist:
                raise NotFavorite

        elif request.method == "POST":
            try:
                UserFavoriteRecipes.objects.create(
                    user=request.user,
                    recipe=Recipe.objects.get(pk=pk)
                )
                serializer = RecipeSerializer(
                    recipe,
                    context={'request': request}
                )
                return Response(serializer.data, status.HTTP_201_CREATED)
            except IntegrityError:
                raise AlreadyFavorite

    @action(
        detail=False,
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


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
