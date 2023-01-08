from django.urls import path

from .views import (
    users_view,
    token_view,
    set_password,
    current_user,
    profile,
    subscribe,
    my_subscriptions,
)
app_name = 'users'

urlpatterns = [
    path('', users_view),
    path('login/', token_view),
    path('set_password/', set_password),
    path('me/', current_user),
    path('<int:id>/subscribe/', subscribe),
    path('<int:id>/', profile),
    path('subscriptions/', my_subscriptions)
]
