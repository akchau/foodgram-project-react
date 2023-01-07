from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации."
    """

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
        )


class UsersSerializer(serializers.ModelSerializer):
    """
    Список пользователей."
    """

    class Meta:
        model = User
        fields = (
            "email",
            "pk",
            "username",
            "first_name",
            "last_name",
        )


class GetTokenSerializer(serializers.ModelSerializer):
    """
    Запрос токена
    """

    class Meta:
        model = User
        fields = (
            "email",
            "password",
        )
