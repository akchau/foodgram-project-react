from django.contrib.auth import get_user_model
from rest_framework import viewsets

from .models import 

User = get_user_model()

class ReciepeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer


class IngridientViewSet:
    pass


class TagViewSet:
    pass


def download_shopping_cart():
    pass


def shopping_cart():
    pass