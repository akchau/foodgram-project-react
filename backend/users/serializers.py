from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Subscribe

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
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "pk",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        print("Проверяем подписку")
        return Subscribe.objects.filter(
            follower=request.user, following=obj).exists()


class GetTokenSerializer(serializers.ModelSerializer):
    """
    Запрос токена
    """

    class Meta:
        model = User
        fields = (
            "password",
            "email",
        )


class ChangePasswordSerializer(serializers.Serializer):
    """
    Смена пороля
    """
    new_password = serializers.CharField(max_length=200)
    current_password = serializers.CharField(max_length=200)


class CurrentUserSerializer(serializers.ModelSerializer):
    """
    Текущий пользователь
    """
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
        )
