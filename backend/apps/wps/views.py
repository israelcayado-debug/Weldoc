from django.db import transaction
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from . import models
from . import serializers
from apps.users.project_permissions import ProjectScopedPermission


def _parse_range(value):
    if not value:
        return None
    if "-" not in value:
        return None
    parts = [p.strip() for p in value.split("-", 1)]
    try:
        return float(parts[0]), float(parts[1])
    except ValueError:
        return None

class BaseRoleViewSet(viewsets.ModelViewSet):
    permission_classes = [ProjectScopedPermission]
    read_roles = ["Admin", "Supervisor", "Inspector", "Soldador"]
    write_roles = ["Admin", "Supervisor"]


class MaterialBaseViewSet(BaseRoleViewSet):
    queryset = models.MaterialBase.objects.all()
    serializer_class = serializers.MaterialBaseSerializer


class FillerMaterialViewSet(BaseRoleViewSet):
    queryset = models.FillerMaterial.objects.all()
    serializer_class = serializers.FillerMaterialSerializer


class JointTypeViewSet(BaseRoleViewSet):
    queryset = models.JointType.objects.all()
    serializer_class = serializers.JointTypeSerializer


class WpsViewSet(BaseRoleViewSet):
    queryset = models.Wps.objects.all()
    serializer_class = serializers.WpsSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    @action(detail=True, methods=["post"], url_path="submit-review")
    def submit_review(self, request, pk=None):
        wps = self.get_object()
        if wps.status != "draft":
            return Response(
                {"code": "invalid_status", "message": "Only allowed from draft status."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        wps.status = "in_review"
        wps.save(update_fields=["status"])
        return Response(self.get_serializer(wps).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        wps = self.get_object()
        if wps.status not in ("draft", "in_review"):
            return Response(
                {"code": "invalid_status", "message": "Status does not allow approval."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        pqr_ids = request.data.get("pqr_ids", [])
        if not isinstance(pqr_ids, list) or not pqr_ids:
            return Response(
                {"code": "missing_pqr", "message": "pqr_ids is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        pqrs = list(models.Pqr.objects.filter(id__in=pqr_ids))
        if len(pqrs) != len(pqr_ids):
            return Response(
                {"code": "pqr_not_found", "message": "One or more PQR not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        not_approved = [p.id for p in pqrs if p.status != "approved"]
        if not_approved:
            return Response(
                {"code": "pqr_not_approved", "message": "PQR not approved."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        for pqr in pqrs:
            if pqr.standard != wps.standard:
                return Response(
                    {"code": "standard_mismatch", "message": "WPS/PQR standard does not match."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        wps_vars = {
            v.name: v.value for v in models.WpsVariable.objects.filter(wps=wps)
        }
        pqr_results = {
            r.test_type: r.result for r in models.PqrResult.objects.filter(pqr__in=pqrs)
        }
        for key in ("material_pno", "filler_fno"):
            if key in wps_vars and key in pqr_results and wps_vars[key] != pqr_results[key]:
                return Response(
                    {"code": "value_mismatch", "message": f"{key} does not match PQR."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if "processes" in wps_vars and "processes" in pqr_results:
            wps_procs = {p.strip() for p in wps_vars["processes"].split(",") if p.strip()}
            pqr_procs = {p.strip() for p in pqr_results["processes"].split(",") if p.strip()}
            if not wps_procs.issubset(pqr_procs):
                return Response(
                    {"code": "process_mismatch", "message": "Processes outside PQR."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if "thickness_range" in wps_vars and "thickness_range" in pqr_results:
            wps_range = _parse_range(wps_vars["thickness_range"])
            pqr_range = _parse_range(pqr_results["thickness_range"])
            if wps_range and pqr_range:
                if wps_range[0] < pqr_range[0] or wps_range[1] > pqr_range[1]:
                    return Response(
                        {"code": "thickness_mismatch", "message": "Thickness range outside PQR."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        if "position" in wps_vars and "position" in pqr_results:
            wps_pos = wps_vars["position"].strip()
            pqr_pos = {p.strip() for p in pqr_results["position"].split(",") if p.strip()}
            if wps_pos and pqr_pos and wps_pos not in pqr_pos:
                return Response(
                    {"code": "position_mismatch", "message": "Position outside PQR."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        missing = []
        processes = models.WpsProcess.objects.filter(wps=wps)
        if not processes.exists():
            return Response(
                {"code": "missing_processes", "message": "At least one WPS process is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        for process in processes:
            defs = models.WpsVariableDefinition.objects.filter(
                process_code=process.process_code
            ).filter(
                Q(special_process__isnull=True)
                | Q(special_process="")
                | Q(special_process=process.special_process)
            )
            required_defs = defs.filter(category="essential")
            if wps.impact_test:
                required_defs = required_defs | defs.filter(category="supplementary")
            values = {
                v.definition_id: v.value
                for v in models.WpsVariableValue.objects.filter(wps_process=process)
            }
            for definition in required_defs:
                value = values.get(definition.id)
                if value is None or str(value).strip() == "":
                    missing.append(f"{process.process_code}:{definition.code}")
        if missing:
            return Response(
                {
                    "code": "missing_required_variables",
                    "message": "Required WPS variables are missing.",
                    "missing": missing,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            for pqr in pqrs:
                models.WpsPqrLink.objects.get_or_create(wps=wps, pqr=pqr)
            wps.status = "approved"
            wps.save(update_fields=["status"])
        return Response(self.get_serializer(wps).data)


class PqrViewSet(BaseRoleViewSet):
    queryset = models.Pqr.objects.all()
    serializer_class = serializers.PqrSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(project=None)

    def perform_update(self, serializer):
        serializer.save(project=None)

    @action(detail=True, methods=["post"], url_path="submit-review")
    def submit_review(self, request, pk=None):
        pqr = self.get_object()
        if pqr.status != "draft":
            return Response(
                {"code": "invalid_status", "message": "Only allowed from draft status."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        pqr.status = "in_review"
        pqr.save(update_fields=["status"])
        return Response(self.get_serializer(pqr).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        pqr = self.get_object()
        if pqr.status not in ("draft", "in_review"):
            return Response(
                {"code": "invalid_status", "message": "Status does not allow approval."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        results = models.PqrResult.objects.filter(pqr=pqr)
        if not results.exists():
            return Response(
                {"code": "missing_results", "message": "PQR has no results."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        pqr.status = "approved"
        pqr.save(update_fields=["status"])
        return Response(self.get_serializer(pqr).data)


class WpsPqrLinkViewSet(BaseRoleViewSet):
    queryset = models.WpsPqrLink.objects.all()
    serializer_class = serializers.WpsPqrLinkSerializer


class WpsVariableViewSet(BaseRoleViewSet):
    queryset = models.WpsVariable.objects.all()
    serializer_class = serializers.WpsVariableSerializer


class WpsProcessViewSet(BaseRoleViewSet):
    queryset = models.WpsProcess.objects.all()
    serializer_class = serializers.WpsProcessSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        wps_id = self.request.query_params.get("wps_id")
        if wps_id:
            qs = qs.filter(wps_id=wps_id)
        return qs


class WpsVariableDefinitionViewSet(BaseRoleViewSet):
    queryset = models.WpsVariableDefinition.objects.all()
    serializer_class = serializers.WpsVariableDefinitionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        process_code = self.request.query_params.get("process_code")
        special_process = self.request.query_params.get("special_process")
        if process_code:
            qs = qs.filter(process_code=process_code)
        if special_process is not None:
            qs = qs.filter(special_process=special_process)
        return qs


class WpsVariableValueViewSet(BaseRoleViewSet):
    queryset = models.WpsVariableValue.objects.all()
    serializer_class = serializers.WpsVariableValueSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        wps_process_id = self.request.query_params.get("wps_process_id")
        if wps_process_id:
            qs = qs.filter(wps_process_id=wps_process_id)
        return qs


class PqrResultViewSet(BaseRoleViewSet):
    queryset = models.PqrResult.objects.all()
    serializer_class = serializers.PqrResultSerializer

