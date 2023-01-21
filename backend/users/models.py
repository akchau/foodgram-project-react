from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class Custom_User(AbstractUser):
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        validators=[AbstractUser.username_validator],
        error_messages={
            'unique': "A user with that username already exists."
        },
    )
    email = models.EmailField('email address', unique=True)
    first_name = models.CharField('first name', max_length=150)
    last_name = models.CharField('last name', max_length=150)
    password = models.CharField('password', max_length=150)
    following = models.ManyToManyField('self', through='Subscribe')
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


User = get_user_model()


class Subscribe(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
        null=True,
        blank=True,
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Подписка",
        related_name="follower",
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return self.following.username
