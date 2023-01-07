from django.urls import path

from .views import users_view, token_view

app_name = 'users'

urlpatterns = [
    path('', users_view),
    path('login/', token_view)
]
