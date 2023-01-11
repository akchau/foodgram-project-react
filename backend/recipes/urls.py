from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import SimpleRouter


from .views import (
    RecipeViewSet,
    IngridientViewSet,
    TagViewSet,
    download_shopping_cart,
    shopping_cart,


)
app_name = 'recipes'

router = SimpleRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngridientViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('recipes/download_shopping_cart/', download_shopping_cart),
    path('recipes/<int:id>/shopping_cart', shopping_cart),
    path(r'', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
