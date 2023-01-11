from django.contrib import admin

from .models import Tag, Ingridient, Recipe, IngridientRecipe

admin.site.register(Tag)
admin.site.register(Ingridient)
admin.site.register(Recipe)
admin.site.register(IngridientRecipe)
