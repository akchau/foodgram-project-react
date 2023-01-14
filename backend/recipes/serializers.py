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


class IngridientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингридиента
    """
    id = serializers.IntegerField(source='pk', required=False)

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
    id = serializers.Field()
    name = serializers.Field()
    measurement_unit = serializers.Field()

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
    id = serializers.IntegerField(
        source='pk',
        read_only=True
    )

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
    id = serializers.IntegerField(source='pk', required=False)
    author = UsersSerializer(read_only=True, many=False)
    ingridients = IngridientSerializer(read_only=True, many=True)
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
