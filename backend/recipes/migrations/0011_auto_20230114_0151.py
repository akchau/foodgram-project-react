# Generated by Django 3.2.16 on 2023-01-13 22:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_auto_20230114_0132'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingridientrecipe',
            name='amount',
        ),
        migrations.AlterUniqueTogether(
            name='tagrecipe',
            unique_together={('tag', 'recipe')},
        ),
    ]
