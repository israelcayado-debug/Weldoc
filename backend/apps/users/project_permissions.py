from rest_framework import permissions

from apps.projects import models as project_models
from .permissions import RolePermission


class ProjectScopedPermission(RolePermission):
    project_field = "project_id"

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.user.is_superuser:
            return True
        project_id = request.query_params.get("project_id")
        if request.method not in permissions.SAFE_METHODS:
            project_id = request.data.get("project_id") or project_id
        if not project_id:
            return True
        return project_models.ProjectUser.objects.filter(
            project_id=project_id, user__email=request.user.email
        ).exists()
