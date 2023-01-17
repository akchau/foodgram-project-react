from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    token_view,
    set_password,
    subscribe,
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
    path('auth/token/login/', token_view),
    path('users/set_password/', set_password),
    path('users/<int:id>/subscribe/', subscribe),
    path('', include(router.urls)),
]
