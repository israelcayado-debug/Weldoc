from rest_framework import viewsets
from . import models
from . import serializers
from apps.users.project_permissions import ProjectScopedPermission

class BaseRoleViewSet(viewsets.ModelViewSet):
    permission_classes = [ProjectScopedPermission]
    read_roles = ["Admin", "Supervisor", "Inspector"]
    write_roles = ["Admin", "Supervisor"]


class ReportViewSet(BaseRoleViewSet):
    queryset = models.Report.objects.all()
    serializer_class = serializers.ReportSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs


class DossierViewSet(BaseRoleViewSet):
    queryset = models.Dossier.objects.all()
    serializer_class = serializers.DossierSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs


class ImportJobViewSet(BaseRoleViewSet):
    queryset = models.ImportJob.objects.all()
    serializer_class = serializers.ImportJobSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        created_by = self.request.query_params.get("created_by")
        if created_by:
            qs = qs.filter(created_by_id=created_by)
        return qs


class ImportErrorViewSet(BaseRoleViewSet):
    queryset = models.ImportError.objects.all()
    serializer_class = serializers.ImportErrorSerializer

