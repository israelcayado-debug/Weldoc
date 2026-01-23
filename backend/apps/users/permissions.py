from rest_framework import permissions

from . import models


class RolePermission(permissions.BasePermission):
    read_roles = ["Admin", "Supervisor", "Inspector", "Soldador"]
    write_roles = ["Admin", "Supervisor"]

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            app_user = models.User.objects.get(email=request.user.email)
        except models.User.DoesNotExist:
            return False
        roles = models.UserRole.objects.filter(user=app_user).values_list(
            "role__name", flat=True
        )
        if request.method in permissions.SAFE_METHODS:
            allowed = getattr(view, "read_roles", self.read_roles)
        else:
            allowed = getattr(view, "write_roles", self.write_roles)
        return any(role in allowed for role in roles)
