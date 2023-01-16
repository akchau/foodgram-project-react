import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import (
    Ingredient,
    Tag,
    Recipe,
    IngredientRecipe,
    UserFavoriteRecipes,
    UserShoppingCartRecipes,
)
from users.serializers import UsersSerializer
import webcolors

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингридиента
    """
    id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингридиента в рецепте.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe

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
    Сериализатор тега
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


class IngredientsEditSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    image = Base64ImageField(required=True, allow_null=False)
    author = UsersSerializer(read_only=True, many=False)
    ingredients = IngredientsEditSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "ingredients",
            "author",
            "name",
            "text",
            "cooking_time",
            "image",
        )

    def validate(self, data):
        return data

    def create(self, validated_data):
        """Создание рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        IngredientRecipe.objects.bulk_create(
            [
                IngredientRecipe(
                    recipe=recipe,
                    ingredient=get_object_or_404(
                        Ingredient,
                        id=ingr.get('id')),
                    amount=ingr.get('amount')
                )
                for ingr in ingredients
            ]
        )
        return recipe

    def update(self, recipe, validated_data):
        """Обновление рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe.tags.set(tags)
        IngredientRecipe.objects.filter(recipe=recipe).delete()
        print('Пришли')
        IngredientRecipe.objects.bulk_create(
            [
                IngredientRecipe(
                    recipe=recipe,
                    ingredient=get_object_or_404(
                        Ingredient,
                        id=ingr.get('id')),
                    amount=ingr.get('amount')
                )
                for ingr in ingredients
            ]
        )

        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецепта.
    """
    id = serializers.IntegerField(source='pk')
    author = UsersSerializer(read_only=True, many=False)
    ingredients = IngredientInRecipeSerializer(
        source='ingredientrecipe_set', many=True)
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
            "ingredients",
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
    Сериализатор рецепта в корзине
    """
    sum_amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'sum_amount', 'measurement_unit')

    def get_sum_amount(self, obj):
        return obj.sum_amount
