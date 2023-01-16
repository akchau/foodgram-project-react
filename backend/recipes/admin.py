from django.contrib import admin

from .models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientRecipe,
    UserFavoriteRecipes,
    UserShoppingCartRecipes,
    TagRecipe,
)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1
    fields = ('ingredient', 'amount')


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    min_num = 1
    fields = ('tag',)


class TagAdmin(admin.ModelAdmin):
    empty_value_display = '-empty-'
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    empty_value_display = '-empty-'
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name', )


class RecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-empty-'
    inlines = [IngredientRecipeInline, TagRecipeInline]
    list_display = (
        'name',
        'author',
    )
    fields = (
        "author",
        "name",
        "text",
        "cooking_time",
        "image",
    )
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags',)

    """
    def has_add_permission(self, request, obj=None):
        return False
    """


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(UserFavoriteRecipes)
admin.site.register(UserShoppingCartRecipes)
admin.site.register(TagRecipe)
