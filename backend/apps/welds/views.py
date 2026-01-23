from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from . import models
from . import serializers
from apps.users.project_permissions import ProjectScopedPermission

class BaseRoleViewSet(viewsets.ModelViewSet):
    permission_classes = [ProjectScopedPermission]
    read_roles = ["Admin", "Supervisor", "Inspector", "Soldador"]
    write_roles = ["Admin", "Supervisor"]


class DrawingViewSet(BaseRoleViewSet):
    queryset = models.Drawing.objects.all()
    serializer_class = serializers.DrawingSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs


class WeldMapViewSet(BaseRoleViewSet):
    queryset = models.WeldMap.objects.all()
    serializer_class = serializers.WeldMapSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    @action(detail=True, methods=["post"], url_path="marks")
    def marks(self, request, pk=None):
        weld_map = self.get_object()
        marks = request.data.get("marks", [])
        if not isinstance(marks, list) or not marks:
            return Response(
                {"code": "missing_marks", "message": "Debe incluir marks."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        created = 0
        with transaction.atomic():
            for mark in marks:
                number = mark.get("number")
                geometry = mark.get("geometry")
                if not number or not geometry:
                    return Response(
                        {"code": "invalid_mark", "message": "number y geometry requeridos."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                weld, _ = models.Weld.objects.get_or_create(
                    project=weld_map.project,
                    number=number,
                    defaults={"drawing": weld_map.drawing, "status": "planned"},
                )
                models.WeldMark.objects.create(
                    weld_map=weld_map,
                    weld=weld,
                    geometry=geometry,
                )
                for attr in mark.get("attributes", []):
                    name = attr.get("name")
                    value = attr.get("value")
                    if name and value is not None:
                        models.WeldAttribute.objects.create(
                            weld=weld, name=name, value=str(value)
                        )
                created += 1
        return Response({"created": created})


class WeldViewSet(BaseRoleViewSet):
    queryset = models.Weld.objects.all()
    serializer_class = serializers.WeldSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        status_param = self.request.query_params.get("status")
        if project_id:
            qs = qs.filter(project_id=project_id)
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        weld = self.get_object()
        if weld.status not in ("planned", "in_progress", "repair"):
            return Response(
                {"code": "invalid_status", "message": "Estado no permite cerrar."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        last_post = (
            models.VisualInspection.objects.filter(weld=weld, stage="post_weld")
            .order_by("-at")
            .first()
        )
        if last_post and last_post.result == "fail":
            return Response(
                {"code": "post_weld_fail", "message": "Inspeccion post_weld en fail."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        closed_at = request.data.get("closed_at")
        if closed_at:
            closed_at = timezone.datetime.fromisoformat(closed_at.replace("Z", "+00:00"))
        else:
            closed_at = timezone.now()

        with transaction.atomic():
            weld.status = "completed"
            weld.closed_at = closed_at
            weld.save(update_fields=["status", "closed_at"])

            assignments = models.WeldWelderAssignment.objects.filter(
                weld=weld, status="active"
            )
            wps_assignment = (
                models.WeldWpsAssignment.objects.filter(weld=weld, status="active")
                .order_by("-assigned_at")
                .first()
            )
            process = "unknown"
            if wps_assignment:
                var = (
                    models.wps.WpsVariable.objects.filter(
                        wps=wps_assignment.wps, name="processes"
                    )
                    .order_by("id")
                    .first()
                )
                if var and var.value:
                    process = var.value.split(",")[0].strip()

            for assign in assignments:
                models.wpq.ContinuityLog.objects.create(
                    welder=assign.welder,
                    weld=weld,
                    date=closed_at.date(),
                    process=process or "unknown",
                )
                continuity, _ = models.wpq.WelderContinuity.objects.get_or_create(
                    welder=assign.welder
                )
                continuity.last_activity_date = closed_at.date()
                continuity.continuity_due_date = closed_at.date() + timezone.timedelta(
                    days=180
                )
                continuity.status = "in_continuity"
                continuity.save()

        return Response(self.get_serializer(weld).data)


class WeldMarkViewSet(BaseRoleViewSet):
    queryset = models.WeldMark.objects.all()
    serializer_class = serializers.WeldMarkSerializer


class WeldAttributeViewSet(BaseRoleViewSet):
    queryset = models.WeldAttribute.objects.all()
    serializer_class = serializers.WeldAttributeSerializer


class WeldAttributeCatalogViewSet(BaseRoleViewSet):
    queryset = models.WeldAttributeCatalog.objects.all()
    serializer_class = serializers.WeldAttributeCatalogSerializer


class WeldMaterialViewSet(BaseRoleViewSet):
    queryset = models.WeldMaterial.objects.all()
    serializer_class = serializers.WeldMaterialSerializer


class WeldConsumableViewSet(BaseRoleViewSet):
    queryset = models.WeldConsumable.objects.all()
    serializer_class = serializers.WeldConsumableSerializer


class VisualInspectionViewSet(BaseRoleViewSet):
    queryset = models.VisualInspection.objects.all()
    serializer_class = serializers.VisualInspectionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        weld_id = self.request.query_params.get("weld_id")
        if weld_id:
            qs = qs.filter(weld_id=weld_id)
        return qs


class WeldWpsAssignmentViewSet(BaseRoleViewSet):
    queryset = models.WeldWpsAssignment.objects.all()
    serializer_class = serializers.WeldWpsAssignmentSerializer


class WeldWelderAssignmentViewSet(BaseRoleViewSet):
    queryset = models.WeldWelderAssignment.objects.all()
    serializer_class = serializers.WeldWelderAssignmentSerializer


class WorkPackViewSet(BaseRoleViewSet):
    queryset = models.WorkPack.objects.all()
    serializer_class = serializers.WorkPackSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs


class TravelerViewSet(BaseRoleViewSet):
    queryset = models.Traveler.objects.all()
    serializer_class = serializers.TravelerSerializer

