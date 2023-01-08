from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
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
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']


class Subscribe(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
    )

    class Meta:
        unique_together = ('follower', 'following')
