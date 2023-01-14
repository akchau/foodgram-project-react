from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingridient(models.Model):
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
    )
    name = models.CharField(max_length=200)
    text = models.TextField()
    cooking_time = models.IntegerField()
#    image = models.ImageField(
#         "Картинка",
#         upload_to='recipes',
#         blank=True,
#     )
    tags = models.ManyToManyField(Tag, through='TagRecipe')
    ingridients = models.ManyToManyField(
        Ingridient,
        through='IngridientRecipe'
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

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


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.tag.name}-{self.recipe.name}'

    class Meta:
        verbose_name = "Тег рецепта"
        verbose_name_plural = "Теги рецептов"
        unique_together = ('tag', 'recipe')


class IngridientRecipe(models.Model):
    ingridient = models.ForeignKey(
        Ingridient,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    amount = models.SmallIntegerField()

    class Meta:
        unique_together = ('ingridient', 'recipe')
        verbose_name = "Ингридиент в рецепте"
        verbose_name_plural = "Ингридиенты в рецептах"

    def __str__(self):
        return f'{self.recipe}/{self.ingridient} {self.amount} {self.ingridient.measurement_unit}'


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

    def __str__(self):
        return f'Рецепт - {self.recipe} в корзине у {self.user}'
