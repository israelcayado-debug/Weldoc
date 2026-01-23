from rest_framework import permissions, viewsets
from . import models
from . import serializers


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return models.UserRole.objects.filter(
            user_id=request.user.id, role__name="Admin"
        ).exists()

class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class RoleViewSet(viewsets.ModelViewSet):
    queryset = models.Role.objects.all()
    serializer_class = serializers.RoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = models.Permission.objects.all()
    serializer_class = serializers.PermissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = models.UserRole.objects.all()
    serializer_class = serializers.UserRoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = models.RolePermission.objects.all()
    serializer_class = serializers.RolePermissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = models.Notification.objects.all()
    serializer_class = serializers.NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

