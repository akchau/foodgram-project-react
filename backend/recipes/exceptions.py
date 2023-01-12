from rest_framework.exceptions import APIException
from rest_framework import status


class NotFavorite(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Рецепт не добавлен в избранное.'
    default_code = 'errors'


class AlreadyFavorite(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Уже в избранном.'
    default_code = 'errors'


class NotInCart(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Такого рецепта нет в корзине.'
    default_code = 'errors'


class NotRules(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'У вас недостаточно прав для выполнения данного действия.'
    default_code = 'detail'
