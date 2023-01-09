from rest_framework import serializers

from .models import Ingridient


class IngridientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингридиента
    """
    id = serializers.IntegerField(source='pk', required=False)

    class Meta:
        model = Ingridient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )
