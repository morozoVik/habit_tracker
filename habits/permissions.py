from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Разрешение только для владельца объекта"""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsPublic(permissions.BasePermission):
    """Разрешение только для публичных привычек (чтение)"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.is_public or obj.user == request.user
        return obj.user == request.user
