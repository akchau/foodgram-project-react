from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingridient(models.Model):
    name = models.CharField(
        "Название",
        max_length=200
    )
    measurement_unit = models.CharField(
        "Еденица измерения",
        max_length=10
    )


class Tag(models.Model):
    pass


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="recipes",
    )
    name = models.CharField(max_length=200)
    text = models.TextField()
    cooking_time = models.IntegerField()
    image = models.ImageField()

    @property
    def is_favorited(self, request):
        return UserFavoriteRecipes.objects.get(
            recipe=self,
            user=request.user,
        ).exists()

    @property
    def is_in_shopping_cart(self, request):
        return UserShoppingCartRecipes.objects.get(
            recipe=self,
            user=request.user,
        ).exists()


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        related_name="recipes",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        related_name="tags",
    )


class IngridientRecipe(models.Model):
    ingridient = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        related_name="recipes",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        related_name="ingridients",
    )
    amount = models.IntegerField()


class UserFavoriteRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="users_favorite",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipe_favorite",
    )


class UserShoppingCartRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="users_shopping",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipe_shopping",
    )
