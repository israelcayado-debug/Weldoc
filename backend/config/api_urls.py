from rest_framework.routers import DefaultRouter
from django.urls import path

from apps.documents import views as documents_views
from apps.integrations import views as integrations_views
from apps.projects import views as projects_views
from apps.quality import views as quality_views
from apps.reports import views as reports_views
from apps.reports import api as reports_api
from apps.users import views as users_views
from apps.welds import views as welds_views
from apps.wps import views as wps_views
from apps.wpq import views as wpq_views


router = DefaultRouter()

router.register("users", users_views.UserViewSet)
router.register("roles", users_views.RoleViewSet)
router.register("permissions", users_views.PermissionViewSet)
router.register("user-roles", users_views.UserRoleViewSet)
router.register("role-permissions", users_views.RolePermissionViewSet)
router.register("notifications", users_views.NotificationViewSet)

router.register("schema-versions", projects_views.SchemaVersionViewSet)
router.register("clients", projects_views.ClientViewSet)
router.register("projects", projects_views.ProjectViewSet)
router.register("project-users", projects_views.ProjectUserViewSet)
router.register("project-equipment", projects_views.ProjectEquipmentViewSet)
router.register("audit-logs", projects_views.AuditLogViewSet)
router.register("audit-events", projects_views.AuditEventViewSet)
router.register("numbering-rules", projects_views.NumberingRuleViewSet)

router.register("documents", documents_views.DocumentViewSet)
router.register("document-revisions", documents_views.DocumentRevisionViewSet)
router.register("document-approvals", documents_views.DocumentApprovalViewSet)
router.register("document-signatures", documents_views.DocumentSignatureViewSet)

router.register("materials-base", wps_views.MaterialBaseViewSet)
router.register("materials-filler", wps_views.FillerMaterialViewSet)
router.register("joint-types", wps_views.JointTypeViewSet)
router.register("wps", wps_views.WpsViewSet)
router.register("pqr", wps_views.PqrViewSet)
router.register("wps-pqr-links", wps_views.WpsPqrLinkViewSet)
router.register("wps-variables", wps_views.WpsVariableViewSet)
router.register("wps-processes", wps_views.WpsProcessViewSet)
router.register("wps-variable-definitions", wps_views.WpsVariableDefinitionViewSet)
router.register("wps-variable-values", wps_views.WpsVariableValueViewSet)
router.register("pqr-results", wps_views.PqrResultViewSet)

router.register("welders", wpq_views.WelderViewSet)
router.register("wpq", wpq_views.WpqViewSet)
router.register("wpq-processes", wpq_views.WpqProcessViewSet)
router.register("wpq-tests", wpq_views.WpqTestViewSet)
router.register("continuity-logs", wpq_views.ContinuityLogViewSet)
router.register("expiry-alerts", wpq_views.ExpiryAlertViewSet)
router.register("welder-continuity", wpq_views.WelderContinuityViewSet)

router.register("drawings", welds_views.DrawingViewSet)
router.register("weld-maps", welds_views.WeldMapViewSet)
router.register("welds", welds_views.WeldViewSet)
router.register("weld-marks", welds_views.WeldMarkViewSet)
router.register("weld-attributes", welds_views.WeldAttributeViewSet)
router.register("weld-attribute-catalog", welds_views.WeldAttributeCatalogViewSet)
router.register("weld-materials", welds_views.WeldMaterialViewSet)
router.register("weld-consumables", welds_views.WeldConsumableViewSet)
router.register("visual-inspections", welds_views.VisualInspectionViewSet)
router.register("weld-wps-assignments", welds_views.WeldWpsAssignmentViewSet)
router.register("weld-welder-assignments", welds_views.WeldWelderAssignmentViewSet)
router.register("work-packs", welds_views.WorkPackViewSet)
router.register("travelers", welds_views.TravelerViewSet)

router.register("validation-rulesets", quality_views.ValidationRuleSetViewSet)
router.register("validation-rules", quality_views.ValidationRuleViewSet)
router.register("validation-ruleset-items", quality_views.ValidationRuleSetItemViewSet)
router.register("nde-requests", quality_views.NdeRequestViewSet)
router.register("nde-results", quality_views.NdeResultViewSet)
router.register("pwht-records", quality_views.PwhtRecordViewSet)
router.register("pressure-tests", quality_views.PressureTestViewSet)
router.register("nde-sampling-rules", quality_views.NdeSamplingRuleViewSet)

router.register("reports", reports_views.ReportViewSet)
router.register("dossiers", reports_views.DossierViewSet)
router.register("import-jobs", reports_views.ImportJobViewSet)
router.register("import-errors", reports_views.ImportErrorViewSet)

router.register("integrations", integrations_views.IntegrationEndpointViewSet)
router.register("integration-events", integrations_views.IntegrationEventViewSet)


urlpatterns = router.urls + [
    path("reports/progress", reports_api.ProgressReportView.as_view()),
    path("reports/expiry", reports_api.ExpiryReportView.as_view()),
    path("exports/welding-list", reports_api.ExportWeldingListView.as_view()),
    path("exports/qualifications", reports_api.ExportQualificationsView.as_view()),
    path("exports/dossier", reports_api.ExportDossierView.as_view()),
    path("exports/<uuid:export_id>", reports_api.ExportStatusView.as_view()),
    path("exports/<uuid:export_id>/download", reports_api.ExportDownloadView.as_view()),
]
