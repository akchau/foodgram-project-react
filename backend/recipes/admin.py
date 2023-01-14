from django.contrib import admin

from .models import (
    Tag,
    Ingridient,
    Recipe,
    IngridientRecipe,
    UserFavoriteRecipes,
    UserShoppingCartRecipes,
    TagRecipe,
)


class IngridientRecipeInline(admin.TabularInline):
    model = IngridientRecipe
    min_num = 1
    fields = ('ingridient', 'amount')


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    min_num = 1
    fields = ('tag',)


class TagAdmin(admin.ModelAdmin):
    empty_value_display = '-empty-'
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')


class IngridientAdmin(admin.ModelAdmin):
    empty_value_display = '-empty-'
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name', )


class RecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-empty-'
    inlines = [IngridientRecipeInline, TagRecipeInline]
    list_display = (
        'name',
        'author',
    )
    fields = (
        "author",
        "name",
        "text",
        "cooking_time",
        "recipe_in_favorite",
        )
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags',)

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingridient, IngridientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngridientRecipe)
admin.site.register(UserFavoriteRecipes)
admin.site.register(UserShoppingCartRecipes)
admin.site.register(TagRecipe)
