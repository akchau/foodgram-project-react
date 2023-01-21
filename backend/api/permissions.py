from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if (request.method in permissions.SAFE_METHODS
           or request.user.is_superuser
           or obj.author == request.user):
            return True
        return False


class AdminAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Permission на уровне объекта, чтобы разрешить редактирование
    только автору объекта, администратору или модератору"""
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user == obj.author)
            or request.user.is_staff
        )


class AdminOrReadOnly(permissions.BasePermission):
    """Permission на уровне объекта, чтобы разрешить редактирование
    только для админов. Остальным - чтение объекта."""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class OwnerUserOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Разрешение на изменение только для админа и пользователя.
    Остальным только чтение объекта.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in ('GET',)
            or (request.user == obj)
            or request.user.is_admin
        )
