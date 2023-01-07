from django.urls import path, include

from .views import (
    users_view,
    token_view,
    set_password,
    current_user,
    profile,
    MyTokenDestroyView
)
app_name = 'users'

urlpatterns = [
    path('', users_view),
    path('login/', token_view),
    path('set_password/', set_password),
    path('me/', current_user),
    path('<int:pk>/', profile),
]
