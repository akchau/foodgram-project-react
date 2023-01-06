from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .serializers import (
    RegistrationSerializer,
    UsersSerializer
)
User = get_user_model()


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def users_view(request):
    """
    Функция создает пользователя и
    отправляет ему на почту код подтверждения.
    """
    if request.method == "POST":
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    users = User.objects.all()
    serializer = UsersSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
