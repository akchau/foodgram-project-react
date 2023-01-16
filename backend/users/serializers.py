from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Subscribe

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации
    """
    id = serializers.ReadOnlyField(source='pk')
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "id",
            "email",
            "first_name",
            "last_name",
        )


class UsersSerializer(serializers.ModelSerializer):
    """
    Список пользователей
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        """Метод добавляет поле is_subscribed в ответ."""
        request = self.context.get("request")
        if request.user.is_authenticated:
            return Subscribe.objects.filter(
                follower=request.user, following=obj).exists()
        return False


class GetTokenSerializer(serializers.Serializer):
    """
    Запрос токена
    """
    email = serializers.EmailField()
    password = serializers.CharField(max_length=150)


class ChangePasswordSerializer(serializers.Serializer):
    """
    Смена пороля
    """
    new_password = serializers.CharField(max_length=150)
    current_password = serializers.CharField(max_length=150)
