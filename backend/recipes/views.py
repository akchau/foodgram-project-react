from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.response import Response

from .models import Tag, Ingridient, Recipe
from .serializers import TagSerializer, IngridientSerializer, RecipeSerializer

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class IngridientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


def download_shopping_cart():
    pass


def shopping_cart():
    pass
