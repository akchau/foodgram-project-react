from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        "Название",
        max_length=200,
        unique=True,
    )
    measurement_unit = models.CharField(
        "Еденица измерения",
        max_length=10
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"


class Tag(models.Model):
    name = models.CharField(
        "Название",
        max_length=50,
        unique=True,
    )
    color = models.CharField(
        "Цвет тега",
        max_length=10,
        unique=True,
    )
    slug = models.SlugField(
        "slug-тега",
        unique=True,
    )

    class Meta:
        unique_together = ('name', 'slug')
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор публикации"
    )
    name = models.CharField("Название", max_length=200)
    text = models.TextField("Текстовое описание")
    cooking_time = models.PositiveIntegerField("Время готовки")
    image = models.ImageField(
        "Картинка",
        upload_to='recipes',
    )
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe'
    )
    pub_date = models.DateTimeField(
        "Дата добавления",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ['-pub_date']

    def __str__(self):
        return self.name

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


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингридиент"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )
    amount = models.PositiveIntegerField("Количество")

    class Meta:
        unique_together = ('ingredient', 'recipe')
        verbose_name = "Ингридиент в рецепте"
        verbose_name_plural = "Ингридиенты в рецептах"

    def __str__(self):
        return (f'{self.recipe}/{self.ingredient} '
                f'{self.amount} {self.ingredient.measurement_unit}')


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

    class Meta:
        unique_together = ('recipe', 'user')
        verbose_name = "Рецепт в избранном"
        verbose_name_plural = "Рецепты в избранном"

    def __str__(self):
        return self.recipe.name


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

    class Meta:
        verbose_name = "Рецепт в корзине"
        verbose_name_plural = "Рецепты в корзине"
        unique_together = ('recipe', 'user')

    def __str__(self):
        return f'Рецепт - {self.recipe} в корзине у {self.user}'
