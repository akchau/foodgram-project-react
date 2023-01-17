import base64
import webcolors

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    IngredientRecipe,
    UserFavoriteRecipes,
    UserShoppingCartRecipes,
)
from users.models import Subscribe, User


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации
    """
    id = serializers.ReadOnlyField(source='pk')
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "id",
            "email",
            "first_name",
            "last_name",
        )


class UsersSerializer(serializers.ModelSerializer):
    """
    Список пользователей
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        """Метод добавляет поле is_subscribed в ответ."""
        request = self.context.get("request")
        if request.user.is_authenticated:
            return Subscribe.objects.filter(
                follower=request.user, following=obj).exists()
        return False


class GetTokenSerializer(serializers.Serializer):
    """
    Запрос токена
    """
    email = serializers.EmailField()
    password = serializers.CharField(max_length=150)


class ChangePasswordSerializer(serializers.Serializer):
    """
    Смена пороля
    """
    new_password = serializers.CharField(max_length=150)
    current_password = serializers.CharField(max_length=150)


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
        tags = data["tags"]
        tag_list = []
        if not data["tags"]:
            raise serializers.ValidationError('Теги обязательны для рецептов')
        for items in tags:
            if items in tag_list:
                raise serializers.ValidationError(
                    'Тег должен быть уникальным')
            tag_list.append(items)

        ingredients = data["ingredients"]
        ingredient_list = []
        if not data["ingredients"]:
            raise serializers.ValidationError(
                'Ингридиенты обызательны для рецептов')
        for items in ingredients:
            if items['id'] < 0:
                raise serializers.ValidationError(
                    'id не может быть отрицательным числом')
            try:
                ingredient = Ingredient.objects.get(id=items['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    'Такого ингридиента не существует')
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингридиент должен быть уникальным')
            ingredient_list.append(ingredient)
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
                        pk=ingr.get('id')),
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
