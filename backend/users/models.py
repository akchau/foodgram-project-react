from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    def get_hello(self):
        return "hello"
