from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from . import models
from . import serializers
from apps.users.project_permissions import ProjectScopedPermission


def _parse_range(value):
    if not value or "-" not in value:
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


class WpqViewSet(BaseRoleViewSet):
    queryset = models.Wpq.objects.all()
    serializer_class = serializers.WpqSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        welder_id = self.request.query_params.get("welder_id")
        project_id = self.request.query_params.get("project_id")
        if welder_id:
            qs = qs.filter(welder_id=welder_id)
        if project_id:
            qs = qs.filter(
                welder__continuitylog__weld__project_id=project_id
            ).distinct()
        return qs

    @action(detail=True, methods=["post"], url_path="submit-review")
    def submit_review(self, request, pk=None):
        wpq = self.get_object()
        if wpq.status != "draft":
            return Response(
                {"code": "invalid_status", "message": "Solo se permite desde draft."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        wpq.status = "in_review"
        wpq.save(update_fields=["status"])
        return Response(self.get_serializer(wpq).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        wpq = self.get_object()
        if wpq.status not in ("draft", "in_review"):
            return Response(
                {"code": "invalid_status", "message": "Status does not allow approval."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not models.WpqProcess.objects.filter(wpq=wpq).exists():
            return Response(
                {"code": "missing_process", "message": "WPQ sin procesos."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        tests = {t.test_type: t.result for t in models.WpqTest.objects.filter(wpq=wpq)}
        proc = models.WpqProcess.objects.filter(wpq=wpq).first()
        if proc:
            if "thickness_range" in tests and proc.thickness_range:
                t_range = _parse_range(tests["thickness_range"])
                p_range = _parse_range(proc.thickness_range)
                if t_range and p_range:
                    if t_range[0] < p_range[0] or t_range[1] > p_range[1]:
                        return Response(
                            {"code": "thickness_mismatch", "message": "Rango de espesor fuera del ensayo."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
            if "position" in tests and proc.positions:
                test_pos = tests["position"].strip()
                proc_pos = {p.strip() for p in proc.positions.split(",") if p.strip()}
                if test_pos and proc_pos and test_pos not in proc_pos:
                    return Response(
                        {"code": "position_mismatch", "message": "Posicion fuera del ensayo."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        wpq.status = "approved"
        wpq.save(update_fields=["status"])
        return Response(self.get_serializer(wpq).data)


class WpqProcessViewSet(BaseRoleViewSet):
    queryset = models.WpqProcess.objects.all()
    serializer_class = serializers.WpqProcessSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(
                wpq__welder__continuitylog__weld__project_id=project_id
            ).distinct()
        return qs


class WpqTestViewSet(BaseRoleViewSet):
    queryset = models.WpqTest.objects.all()
    serializer_class = serializers.WpqTestSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(
                wpq__welder__continuitylog__weld__project_id=project_id
            ).distinct()
        return qs


class ContinuityLogViewSet(BaseRoleViewSet):
    queryset = models.ContinuityLog.objects.all()
    serializer_class = serializers.ContinuityLogSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(weld__project_id=project_id)
        return qs


class ExpiryAlertViewSet(BaseRoleViewSet):
    queryset = models.ExpiryAlert.objects.all()
    serializer_class = serializers.ExpiryAlertSerializer


class WelderContinuityViewSet(BaseRoleViewSet):
    queryset = models.WelderContinuity.objects.all()
    serializer_class = serializers.WelderContinuitySerializer


class WelderViewSet(BaseRoleViewSet):
    queryset = models.Welder.objects.all()
    serializer_class = serializers.WelderSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(continuitylog__weld__project_id=project_id).distinct()
        return qs

    @extend_schema(operation_id="welder_continuity_recalculate_detail")
    @action(
        detail=True,
        methods=["post"],
        url_path="continuity-recalculate",
        url_name="welder-continuity-recalculate",
    )
    def continuity_recalculate(self, request, pk=None):
        welder = self.get_object()
        last = (
            models.ContinuityLog.objects.filter(welder=welder)
            .order_by("-date")
            .first()
        )
        continuity, _ = models.WelderContinuity.objects.get_or_create(welder=welder)
        if not last:
            continuity.last_activity_date = None
            continuity.continuity_due_date = None
            continuity.status = "out_of_continuity"
        else:
            continuity.last_activity_date = last.date
            continuity.continuity_due_date = last.date + timezone.timedelta(days=180)
            continuity.status = (
                "in_continuity"
                if timezone.now().date() <= continuity.continuity_due_date
                else "out_of_continuity"
            )
        continuity.save()
        return Response(serializers.WelderContinuitySerializer(continuity).data)

    @extend_schema(operation_id="welder_continuity_recalculate_batch")
    @action(
        detail=False,
        methods=["post"],
        url_path="continuity-recalculate-batch",
        url_name="welder-continuity-recalculate-batch",
    )
    def continuity_recalculate_batch(self, request):
        scope = request.data.get("scope")
        project_id = request.data.get("project_id")
        if scope not in ("project", "global"):
            return Response(
                {"code": "invalid_scope", "message": "scope invalido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        welders = models.Welder.objects.all()
        if scope == "project":
            if not project_id:
                return Response(
                    {"code": "missing_project", "message": "project_id requerido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            welders = welders.filter(
                continuitylog__weld__project_id=project_id
            ).distinct()
        results = []
        for welder in welders:
            last = (
                models.ContinuityLog.objects.filter(welder=welder)
                .order_by("-date")
                .first()
            )
            continuity, _ = models.WelderContinuity.objects.get_or_create(
                welder=welder
            )
            if not last:
                continuity.last_activity_date = None
                continuity.continuity_due_date = None
                continuity.status = "out_of_continuity"
            else:
                continuity.last_activity_date = last.date
                continuity.continuity_due_date = last.date + timezone.timedelta(days=180)
                continuity.status = (
                    "in_continuity"
                    if timezone.now().date() <= continuity.continuity_due_date
                    else "out_of_continuity"
                )
            continuity.save()
            results.append(continuity)
        serializer = serializers.WelderContinuitySerializer(results, many=True)
        return Response(serializer.data)

    @extend_schema(operation_id="welder_continuity_recalculate_batch_legacy")
    @action(
        detail=False,
        methods=["post"],
        url_path="continuity-recalculate",
        url_name="welder-continuity-recalculate-batch-legacy",
    )
    def continuity_recalculate_batch_legacy(self, request):
        return self.continuity_recalculate_batch(request)

