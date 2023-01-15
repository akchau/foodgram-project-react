from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import (
    Ingridient,
    Tag,
    Recipe,
    IngridientRecipe,
    UserFavoriteRecipes,
    UserShoppingCartRecipes,
)
from users.serializers import UsersSerializer

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
    id = serializers.ReadOnlyField(source='ingridient.pk')
    name = serializers.Field(source='ingridient.name')
    measurement_unit = serializers.Field(source='ingridient.measurement_unit')

    class Meta:
        model = IngridientRecipe
        fields = (
            "id",
            "name",
            "amount",
            "measurement_unit",
        )


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингридиента
    """
    id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецепта.
    """
    id = serializers.ReadOnlyField(source='pk')
    author = UsersSerializer(read_only=True, many=False)
    ingridients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "tags",
            "ingridients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "text",
            "cooking_time",
        )

    def get_ingridients(self, obj):
        qset = IngridientRecipe.objects.filter(recipe=obj)
        serializer = IngridientInRecipeSerializer(qset, many=True)
        return serializer.data

    def get_is_favorited(self, obj):
        return UserFavoriteRecipes.objects.filter(user=obj.author).exists()

    def get_is_in_shopping_cart(self, obj):
        return UserShoppingCartRecipes.objects.filter(user=obj.author).exists()

    def create(self, validated_data):
        request = self.context.get("request")
        author = request.user
        return Recipe(
            author=author,
            name=validated_data.get('name'),
            text=validated_data.get('text'),
            cooking_time=validated_data.get('cooking_time'),
        )

    def update(self, instance, validated_data):
        return instance


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
