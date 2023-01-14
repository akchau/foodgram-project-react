# Generated by Django 3.2.16 on 2023-01-13 19:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20230113_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='ingridients',
            field=models.ManyToManyField(through='recipes.IngridientRecipe', to='recipes.Ingridient'),
        ),
        migrations.AlterField(
            model_name='ingridientrecipe',
            name='ingridient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.ingridient'),
        ),
        migrations.AlterField(
            model_name='ingridientrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe'),
        ),
    ]