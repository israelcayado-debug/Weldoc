from django.db import transaction
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
                {"code": "invalid_status", "message": "Solo se permite desde draft."},
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
                {"code": "invalid_status", "message": "Estado no permite aprobar."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        pqr_ids = request.data.get("pqr_ids", [])
        if not isinstance(pqr_ids, list) or not pqr_ids:
            return Response(
                {"code": "missing_pqr", "message": "Debe incluir pqr_ids."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        pqrs = list(models.Pqr.objects.filter(id__in=pqr_ids))
        if len(pqrs) != len(pqr_ids):
            return Response(
                {"code": "pqr_not_found", "message": "Uno o mas PQR no existen."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        not_approved = [p.id for p in pqrs if p.status != "approved"]
        if not_approved:
            return Response(
                {"code": "pqr_not_approved", "message": "PQR no aprobado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        for pqr in pqrs:
            if pqr.standard != wps.standard:
                return Response(
                    {"code": "standard_mismatch", "message": "Norma WPS/PQR no coincide."},
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
                    {"code": "value_mismatch", "message": f"{key} no coincide con PQR."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if "processes" in wps_vars and "processes" in pqr_results:
            wps_procs = {p.strip() for p in wps_vars["processes"].split(",") if p.strip()}
            pqr_procs = {p.strip() for p in pqr_results["processes"].split(",") if p.strip()}
            if not wps_procs.issubset(pqr_procs):
                return Response(
                    {"code": "process_mismatch", "message": "Procesos fuera del PQR."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if "thickness_range" in wps_vars and "thickness_range" in pqr_results:
            wps_range = _parse_range(wps_vars["thickness_range"])
            pqr_range = _parse_range(pqr_results["thickness_range"])
            if wps_range and pqr_range:
                if wps_range[0] < pqr_range[0] or wps_range[1] > pqr_range[1]:
                    return Response(
                        {"code": "thickness_mismatch", "message": "Rango de espesor fuera del PQR."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        if "position" in wps_vars and "position" in pqr_results:
            wps_pos = wps_vars["position"].strip()
            pqr_pos = {p.strip() for p in pqr_results["position"].split(",") if p.strip()}
            if wps_pos and pqr_pos and wps_pos not in pqr_pos:
                return Response(
                    {"code": "position_mismatch", "message": "Posicion fuera del PQR."},
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

    @action(detail=True, methods=["post"], url_path="submit-review")
    def submit_review(self, request, pk=None):
        pqr = self.get_object()
        if pqr.status != "draft":
            return Response(
                {"code": "invalid_status", "message": "Solo se permite desde draft."},
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
                {"code": "invalid_status", "message": "Estado no permite aprobar."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        results = models.PqrResult.objects.filter(pqr=pqr)
        if not results.exists():
            return Response(
                {"code": "missing_results", "message": "PQR sin resultados."},
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


class PqrResultViewSet(BaseRoleViewSet):
    queryset = models.PqrResult.objects.all()
    serializer_class = serializers.PqrResultSerializer

