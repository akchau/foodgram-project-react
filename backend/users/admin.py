from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscribe

User = get_user_model()


class FollowerInline(admin.TabularInline):
    model = Subscribe
    min_num = 1
    fields = ('follower',)
    fk_name = "following"
    model._meta.verbose_name = 'Подписчик'
    model._meta.verbose_name_plural = 'Подписчики'


class SubscribeInline(admin.TabularInline):
    model = Subscribe
    min_num = 1
    fields = ('following',)
    fk_name = "follower"
    model._meta.verbose_name = 'Подписка пользователя'
    model._meta.verbose_name_plural = 'Подписки пользователя'


@admin.action(description='Блокировать пользователей')
def blocked(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.action(description='Разблокировать пользователей')
def unblocked(modeladmin, request, queryset):
    queryset.update(is_active=True)


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
        "password",
    )
    list_filter = ('username', 'email',)
    actions = [blocked, unblocked]

    def has_change_permission(self, request, obj=None):
        return False


class SubscribeAdmin(admin.ModelAdmin):
    empty_value_display = '-empty-'
    list_display = (
        'pk',
        'follower',
        'following',
    )


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
