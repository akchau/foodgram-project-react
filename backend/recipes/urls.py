from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    ReciepeViewSet,
    IngridientViewSet,
    TagViewSet,
    download_shopping_cart,
    shopping_cart,


)
app_name = 'recipes'

router = SimpleRouter()
router.register(r'recipes', ReciepeViewSet)
router.register(r'ingridients', IngridientViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('recipes/download_shopping_cart/', download_shopping_cart),
    path('recipes/<int:id>/shopping_cart', shopping_cart),
    path(r'', include(router.urls)),
    
]
