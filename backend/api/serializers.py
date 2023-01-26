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
from users.models import User, Subscribe


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
            "password",
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        """Метод добавляет поле is_subscribed в ответ."""
        request = self.context.get("request")
        if request.user.is_authenticated:
            return Subscribe.objects.filter(
                follower=request.user, following=obj).exists()
        return False

    def create(self, validated_data):
        """ Создание нового пользователя"""
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


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

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                    'Время готовки больше 1!')
        return value

    def validate_tags(self, value):
        tag_list = []
        if not value:
            raise serializers.ValidationError('Теги обязательны для рецептов')
        for items in value:
            if items in tag_list:
                raise serializers.ValidationError(
                    'Тег должен быть уникальным')
            tag_list.append(items)
        return value

    def validate_ingredients(self, value):
        ingredient_list = []
        if not value:
            raise serializers.ValidationError(
                'Ингридиенты обызательны для рецептов')
        for items in value:
            if not Ingredient.objects.filter(id=items['id']).exists():
                raise serializers.ValidationError(
                    'Такого ингридиента не существует')
            ingredient = Ingredient.objects.get(id=items['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингридиент должен быть уникальным')
            ingredient_list.append(ingredient)
        return value

    def creating(self, validated_data, recipe=None):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        if not recipe:
            recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        if IngredientRecipe.objects.filter(recipe=recipe).exists():
            IngredientRecipe.objects.filter(recipe=recipe).delete()
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
        return recipe, validated_data

    def create(self, validated_data):
        """Создание рецепта."""
        recipe, validated_data = self.creating(validated_data)
        return recipe

    def update(self, recipe, validated_data):
        """Обновление рецепта."""
        recipe, validated_data = self.creating(validated_data, recipe)
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
        return UserFavoriteRecipes.objects.filter(
            recipe=obj, user=obj.author).exists()

    def get_is_in_shopping_cart(self, obj):
        return UserShoppingCartRecipes.objects.filter(
            recipe=obj, user=obj.author).exists()


class CompactRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class SubscriptionsSerializers(UsersSerializer):
    recipes = CompactRecipeSerializer(read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count"
        )

    def get_is_subscribed(self, obj):
        """Метод добавляет поле is_subscribed в ответ."""
        request = self.context.get("request")
        if request.user.is_authenticated:
            return Subscribe.objects.filter(
                follower=request.user, following=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class UserWithRecipesSerializer(UsersSerializer):
    recipes = CompactRecipeSerializer(many=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "password",
            "recipes"
        )
        extra_kwargs = {'password': {'write_only': True}}
