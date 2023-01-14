from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscribe

User = get_user_model()


class FollowerInline(admin.TabularInline):
    model = Subscribe
    min_num = 1
    fields = ('following', 'user')
    fk_name = "following"
    model._meta.verbose_name = 'Подписчик'
    model._meta.verbose_name_plural = 'Подписчики'


class SubscribeInline(admin.TabularInline):
    model = Subscribe
    min_num = 1
    fields = ('following',)
    fk_name = "user"
    model._meta.verbose_name = 'Подписка пользователя'
    model._meta.verbose_name_plural = 'Подписки пользователя'


class UserAdmin(admin.ModelAdmin):
    inlines = [FollowerInline, SubscribeInline]
    empty_value_display = '-empty-'
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )


class SubscribeAdmin(admin.ModelAdmin):
    empty_value_display = '-empty-'
    list_display = (
        'pk',
        'user',
        'following',
    )


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
