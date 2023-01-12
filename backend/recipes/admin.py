from django.contrib import admin

from .models import Tag, Ingridient, Recipe, IngridientRecipe, UserFavoriteRecipes, UserShoppingCartRecipes

admin.site.register(Tag)
admin.site.register(Ingridient)
admin.site.register(Recipe)
admin.site.register(IngridientRecipe)
admin.site.register(UserFavoriteRecipes)
admin.site.register(UserShoppingCartRecipes)
