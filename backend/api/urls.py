from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    UserViewSet,
    RecipeViewSet,
    IngredientViewSet,
    TagViewSet,
)


app_name = 'users'

router = SimpleRouter()
router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingridients')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
