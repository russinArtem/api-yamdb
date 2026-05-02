from rest_framework import permissions


class IsAdminOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.role == 'admin'
            or request.user.is_superuser
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.role == 'admin'
            or request.user.is_superuser
        )


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, instance):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            instance.author == request.user
            or request.user.role in ('moderator', 'admin')
            or request.user.is_superuser
        )
