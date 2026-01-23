from rest_framework import viewsets
from . import models
from . import serializers
from apps.users.project_permissions import ProjectScopedPermission

class BaseRoleViewSet(viewsets.ModelViewSet):
    permission_classes = [ProjectScopedPermission]
    read_roles = ["Admin", "Supervisor", "Inspector", "Soldador"]
    write_roles = ["Admin", "Supervisor"]


class DocumentViewSet(BaseRoleViewSet):
    queryset = models.Document.objects.all()
    serializer_class = serializers.DocumentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs


class DocumentRevisionViewSet(BaseRoleViewSet):
    queryset = models.DocumentRevision.objects.all()
    serializer_class = serializers.DocumentRevisionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        document_id = self.request.query_params.get("document_id")
        if document_id:
            qs = qs.filter(document_id=document_id)
        return qs


class DocumentApprovalViewSet(BaseRoleViewSet):
    queryset = models.DocumentApproval.objects.all()
    serializer_class = serializers.DocumentApprovalSerializer
    write_roles = ["Admin", "Supervisor", "Inspector"]


class DocumentSignatureViewSet(BaseRoleViewSet):
    queryset = models.DocumentSignature.objects.all()
    serializer_class = serializers.DocumentSignatureSerializer

