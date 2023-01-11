from rest_framework import serializers

from .models import Ingridient, Tag, Recipe, IngridientRecipe
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
    id = serializers.IntegerField(source='pk', required=False)

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
    ingridients = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "author",
            "ingridients",
            "name",
            "text",
            "cooking_time",
        )

    def get_ingridients(self, obj):
        ingridients = IngridientRecipe.objects.filter(recipe=obj)
        return IngridientInRecipeSerializer(ingridients, read_only=True, many=True)
