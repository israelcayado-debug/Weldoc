from datetime import timedelta
from pathlib import Path

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

from apps.welds import models as weld_models
from apps.wpq import models as wpq_models
from apps.wps import models as wps_models
from . import models
from . import serializers


class ProgressReportView(APIView):
    serializer_class = serializers.ProgressReportSerializer

    @extend_schema(responses=serializers.ProgressReportSerializer)
    def get(self, request):
        project_id = request.query_params.get("project_id")
        if not project_id:
            return Response({"code": "missing_project", "message": "project_id requerido."}, status=400)
        qs = weld_models.Weld.objects.filter(project_id=project_id)
        total = qs.count()
        by_status = {
            "planned": qs.filter(status="planned").count(),
            "in_progress": qs.filter(status="in_progress").count(),
            "completed": qs.filter(status="completed").count(),
            "repair": qs.filter(status="repair").count(),
        }
        return Response({"project_id": project_id, "total_welds": total, "by_status": by_status})


class ExpiryReportView(APIView):
    serializer_class = serializers.ExpiryReportSerializer

    @extend_schema(responses=serializers.ExpiryReportSerializer)
    def get(self, request):
        project_id = request.query_params.get("project_id")
        if not project_id:
            return Response({"code": "missing_project", "message": "project_id requerido."}, status=400)
        today = timezone.now().date()
        warn_date = today + timedelta(days=30)
        continuity = wpq_models.WelderContinuity.objects.filter(
            welder__continuitylog__weld__project_id=project_id
        ).distinct()
        expiring = continuity.filter(continuity_due_date__lte=warn_date, status="in_continuity")
        out = continuity.filter(status="out_of_continuity")
        expiring_list = [
            {
                "welder_id": str(c.welder_id),
                "name": c.welder.name,
                "due_date": c.continuity_due_date,
            }
            for c in expiring
        ]
        out_list = [
            {
                "welder_id": str(c.welder_id),
                "name": c.welder.name,
                "last_activity": c.last_activity_date,
            }
            for c in out
        ]
        return Response(
            {
                "project_id": project_id,
                "expiring_30_days": expiring_list,
                "out_of_continuity": out_list,
            }
        )


class ExportWeldingListView(APIView):
    serializer_class = serializers.ExportWeldingListRequestSerializer

    @extend_schema(
        request=serializers.ExportWeldingListRequestSerializer,
        responses=serializers.ExportStatusSerializer,
    )
    def post(self, request):
        project_id = request.data.get("project_id")
        if not project_id:
            return Response({"code": "missing_project", "message": "project_id requerido."}, status=400)
        report = models.Report.objects.create(
            project_id=project_id, type="welding_list", params_json=request.data.get("filters", {})
        )
        welds = weld_models.Weld.objects.filter(project_id=project_id)
        lines = ["number,status"]
        for w in welds:
            lines.append(f"{w.number},{w.status}")
        report.file_path = f"welding_list_{report.id}.csv"
        report.params_json["_csv_content"] = "\n".join(lines)
        report.save(update_fields=["file_path", "params_json"])
        path = Path(settings.MEDIA_ROOT) / report.file_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report.params_json["_csv_content"], encoding="utf-8")
        return Response({"export_id": str(report.id), "status": "ready", "file_path": report.file_path})


class ExportQualificationsView(APIView):
    serializer_class = serializers.ExportQualificationsRequestSerializer

    @extend_schema(
        request=serializers.ExportQualificationsRequestSerializer,
        responses=serializers.ExportStatusSerializer,
    )
    def post(self, request):
        project_id = request.data.get("project_id")
        export_type = request.data.get("type")
        if not project_id or not export_type:
            return Response({"code": "missing_params", "message": "project_id y type requeridos."}, status=400)
        report = models.Report.objects.create(
            project_id=project_id, type=f"qual_{export_type}", params_json={}
        )
        lines = ["code,status"]
        if export_type == "WPS":
            for wps in wps_models.Wps.objects.filter(project_id=project_id):
                lines.append(f"{wps.code},{wps.status}")
        elif export_type == "WPQ":
            for wpq in wpq_models.Wpq.objects.all():
                lines.append(f"{wpq.code},{wpq.status}")
        report.file_path = f"qual_{export_type}_{report.id}.csv"
        report.params_json["_csv_content"] = "\n".join(lines)
        report.save(update_fields=["file_path", "params_json"])
        path = Path(settings.MEDIA_ROOT) / report.file_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report.params_json["_csv_content"], encoding="utf-8")
        return Response({"export_id": str(report.id), "status": "ready", "file_path": report.file_path})


class ExportDossierView(APIView):
    serializer_class = serializers.ExportDossierRequestSerializer

    @extend_schema(
        request=serializers.ExportDossierRequestSerializer,
        responses=serializers.ExportStatusSerializer,
    )
    def post(self, request):
        project_id = request.data.get("project_id")
        include = request.data.get("include", [])
        if not project_id:
            return Response({"code": "missing_project", "message": "project_id requerido."}, status=400)
        dossier = models.Dossier.objects.create(
            project_id=project_id, config_json={"include": include}
        )
        return Response({"export_id": str(dossier.id), "status": "queued"}, status=status.HTTP_202_ACCEPTED)


class ExportStatusView(APIView):
    serializer_class = serializers.ExportStatusSerializer

    @extend_schema(responses=serializers.ExportStatusSerializer)
    def get(self, request, export_id):
        report = models.Report.objects.filter(id=export_id).first()
        if report:
            status_value = "ready" if report.file_path else "queued"
            return Response({"export_id": str(report.id), "status": status_value, "file_path": report.file_path})
        dossier = models.Dossier.objects.filter(id=export_id).first()
        if dossier:
            status_value = "ready" if dossier.file_path else "queued"
            return Response({"export_id": str(dossier.id), "status": status_value, "file_path": dossier.file_path})
        return Response({"code": "not_found", "message": "export_id no existe."}, status=404)


class ExportDownloadView(APIView):
    serializer_class = serializers.ExportStatusSerializer

    @extend_schema(responses=OpenApiTypes.BINARY)
    def get(self, request, export_id):
        report = models.Report.objects.filter(id=export_id).first()
        if report and report.file_path:
            path = Path(settings.MEDIA_ROOT) / report.file_path
            if path.exists():
                resp = HttpResponse(path.read_text(encoding="utf-8"), content_type="text/csv")
                resp["Content-Disposition"] = f"attachment; filename={report.file_path}"
                return resp
        return Response({"code": "not_found", "message": "archivo no disponible."}, status=404)
