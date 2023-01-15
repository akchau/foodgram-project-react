from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .exceptions import NotFavorite, AlreadyFavorite, NotRules, NotInCart
from .models import Tag, Ingridient, Recipe, UserFavoriteRecipes, UserShoppingCartRecipes, IngridientRecipe
from .serializers import TagSerializer, IngridientSerializer, RecipeSerializer, IngridientInRecipeSerializer

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
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
        ingridients = IngridientRecipe.objects.filter(recipe__in=recipes)
        return Response(IngridientInRecipeSerializer(ingridients, many=True).data)


class IngridientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
