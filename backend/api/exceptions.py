from rest_framework.exceptions import APIException, NotFound
from rest_framework import status


class UserNotFound(NotFound):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Страница не найдена.'
    default_code = 'detail'


class NotFollower(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Вы не подписаны.'
    default_code = 'errors'


class AlreadyFollower(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Вы уже подписаны.'
    default_code = 'errors'


class IncorrectPassword(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Учетные данные не были предоставлены.'
    default_code = 'detail'


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


class AlreadyInCart(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Уже в корзине.'
    default_code = 'errors'
