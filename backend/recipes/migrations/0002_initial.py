# Generated by Django 3.2.16 on 2023-01-17 22:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('recipes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='usershoppingcartrecipes',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_shopping', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userfavoriterecipes',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_favorite', to='recipes.recipe'),
        ),
        migrations.AddField(
            model_name='userfavoriterecipes',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_favorite', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tagrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe'),
        ),
        migrations.AddField(
            model_name='tagrecipe',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.tag'),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together={('name', 'slug')},
        ),
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор публикации'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(through='recipes.IngredientRecipe', to='recipes.Ingredient'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='recipes.Tag'),
        ),
        migrations.AddField(
            model_name='ingredientrecipe',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredient', verbose_name='Ингридиент'),
        ),
        migrations.AddField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterUniqueTogether(
            name='usershoppingcartrecipes',
            unique_together={('recipe', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='userfavoriterecipes',
            unique_together={('recipe', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='tagrecipe',
            unique_together={('tag', 'recipe')},
        ),
        migrations.AlterUniqueTogether(
            name='ingredientrecipe',
            unique_together={('ingredient', 'recipe')},
        ),
    ]
