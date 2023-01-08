from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


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
