import csv
from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

TABLES_DICT = {
    Ingredient: 'ingredients.csv'
}


class Command(BaseCommand):
    help = 'Загрузка данных из csv файлов'

    def handle(self, *args, **kwargs):
        for model, base in TABLES_DICT.items():
            with open(
                f'{settings.BASE_DIR}/static/data/{base}',
                'r', encoding='UTF-8'
            ) as csv_file:
                reader = csv.reader(csv_file)
                [model.objects.create(
                    name=data[0],
                    measurement_unit=data[1]
                ) for data in reader]
        self.stdout.write(
            self.style.SUCCESS('Данные ингридиентов успешно загружены')
        )
