from rest_framework.exceptions import APIException, NotFound
from rest_framework import status


class UserNotFound(NotFound):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Страница не найдена.'
    default_code = 'detail'


class NotFollower(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Вы не подписаны.'
    default_code = 'not_follower'


class AlreadyFollower(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Вы уже подписаны.'
    default_code = 'already_follower'


class IncorrectPassword(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Учетные данные не были предоставлены.'
    default_code = 'detail'
