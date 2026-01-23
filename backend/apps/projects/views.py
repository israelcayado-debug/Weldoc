from rest_framework import permissions, viewsets
from . import models
from . import serializers
from apps.users.views import IsAdminRole

class SchemaVersionViewSet(viewsets.ModelViewSet):
    queryset = models.SchemaVersion.objects.all()
    serializer_class = serializers.SchemaVersionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class ClientViewSet(viewsets.ModelViewSet):
    queryset = models.Client.objects.all()
    serializer_class = serializers.ClientSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        qs = super().get_queryset()
        client_id = self.request.query_params.get("client_id")
        if client_id:
            qs = qs.filter(client_id=client_id)
        return qs


class ProjectUserViewSet(viewsets.ModelViewSet):
    queryset = models.ProjectUser.objects.all()
    serializer_class = serializers.ProjectUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = models.AuditLog.objects.all()
    serializer_class = serializers.AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class AuditEventViewSet(viewsets.ModelViewSet):
    queryset = models.AuditEvent.objects.all()
    serializer_class = serializers.AuditEventSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class NumberingRuleViewSet(viewsets.ModelViewSet):
    queryset = models.NumberingRule.objects.all()
    serializer_class = serializers.NumberingRuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

