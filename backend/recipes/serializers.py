import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import (
    Ingridient,
    Tag,
    Recipe,
    TagRecipe,
    IngridientRecipe,
    UserFavoriteRecipes,
    UserShoppingCartRecipes,
)
from users.serializers import UsersSerializer
import webcolors

User = get_user_model()


class IngridientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингридиента
    """
    id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Ingridient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class IngridientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингридиента в рецепте.
    """
    id = serializers.ReadOnlyField(source='ingridient.id')
    name = serializers.ReadOnlyField(source='ingridient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingridient.measurement_unit')

    class Meta:
        model = IngridientRecipe

        fields = ('id', 'name', 'measurement_unit', 'amount')


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        try:
            value = webcolors.normalize_hex(value)
        except ValueError:
            raise serializers.ValidationError("Такого цвета нет.")
        return value


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингридиента
    """
    id = serializers.ReadOnlyField(source='pk')
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializerWrite(serializers.ModelSerializer):
    pass


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецепта.
    """
    id = serializers.ReadOnlyField(source='pk')
    author = UsersSerializer(read_only=True, many=False)
    ingridients = IngridientInRecipeSerializer(
        source='ingridientrecipe_set', many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingridients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "text",
            "cooking_time",
            "image"
        )

    def get_is_favorited(self, obj):
        return UserFavoriteRecipes.objects.filter(user=obj.author).exists()

    def get_is_in_shopping_cart(self, obj):
        return UserShoppingCartRecipes.objects.filter(user=obj.author).exists()


class CompactRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "cooking_time",
        )


class SubscriptionsSerializers(UsersSerializer):
    recipes = CompactRecipeSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes"
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингридиента в рецепте.
    """
    sum_amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingridient
        fields = ('id', 'name', 'sum_amount', 'measurement_unit')

    def get_sum_amount(self, obj):
        return obj.sum_amount
