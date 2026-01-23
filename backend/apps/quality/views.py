from rest_framework import viewsets
from . import models
from . import serializers
from apps.users.project_permissions import ProjectScopedPermission
from rest_framework.decorators import action
from rest_framework.response import Response

class BaseRoleViewSet(viewsets.ModelViewSet):
    permission_classes = [ProjectScopedPermission]
    read_roles = ["Admin", "Supervisor", "Inspector"]
    write_roles = ["Admin", "Supervisor"]


class ValidationRuleSetViewSet(BaseRoleViewSet):
    queryset = models.ValidationRuleSet.objects.all()
    serializer_class = serializers.ValidationRuleSetSerializer
    write_roles = ["Admin"]


class ValidationRuleViewSet(BaseRoleViewSet):
    queryset = models.ValidationRule.objects.all()
    serializer_class = serializers.ValidationRuleSerializer
    write_roles = ["Admin"]


class ValidationRuleSetItemViewSet(BaseRoleViewSet):
    queryset = models.ValidationRuleSetItem.objects.all()
    serializer_class = serializers.ValidationRuleSetItemSerializer
    write_roles = ["Admin"]


class NdeRequestViewSet(BaseRoleViewSet):
    queryset = models.NdeRequest.objects.all()
    serializer_class = serializers.NdeRequestSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    @action(detail=True, methods=["post"], url_path="results")
    def add_result(self, request, pk=None):
        nde_request = self.get_object()
        serializer = serializers.NdeResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(nde_request=nde_request)
        return Response(serializer.data)


class NdeResultViewSet(BaseRoleViewSet):
    queryset = models.NdeResult.objects.all()
    serializer_class = serializers.NdeResultSerializer


class PwhtRecordViewSet(BaseRoleViewSet):
    queryset = models.PwhtRecord.objects.all()
    serializer_class = serializers.PwhtRecordSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        weld_id = self.request.query_params.get("weld_id")
        if weld_id:
            qs = qs.filter(weld_id=weld_id)
        return qs


class PressureTestViewSet(BaseRoleViewSet):
    queryset = models.PressureTest.objects.all()
    serializer_class = serializers.PressureTestSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs


class NdeSamplingRuleViewSet(BaseRoleViewSet):
    queryset = models.NdeSamplingRule.objects.all()
    serializer_class = serializers.NdeSamplingRuleSerializer
    write_roles = ["Admin", "Supervisor"]

