from django.urls import path

from .views import users_view

app_name = 'users'

urlpatterns = [
    path('', users_view)
]
