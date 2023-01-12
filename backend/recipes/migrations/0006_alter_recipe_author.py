# Generated by Django 3.2.16 on 2023-01-12 21:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0005_alter_userfavoriterecipes_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to='users.user'),
            preserve_default=False,
        ),
    ]
