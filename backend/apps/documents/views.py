from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from . import models
from . import serializers
from apps.users.project_permissions import ProjectScopedPermission
from apps.projects import models as project_models
from apps.users import models as user_models


def _resolve_app_user(request):
    email = getattr(request.user, "email", None) or getattr(request.user, "username", None)
    if not email:
        return None
    return user_models.User.objects.filter(email=email).first()


def _log_audit(action, entity, entity_id, request, diff=None):
    user = _resolve_app_user(request)
    if not user:
        return
    project_models.AuditLog.objects.create(
        entity=entity,
        entity_id=entity_id,
        action=action,
        user=user,
        diff_json=diff or {},
    )

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

    @action(detail=True, methods=["post"], url_path="submit-review")
    def submit_review(self, request, pk=None):
        revision = self.get_object()
        if revision.status != "draft":
            return Response(
                {"code": "invalid_status", "message": "Solo se permite desde draft."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        revision.status = "in_review"
        revision.save(update_fields=["status"])
        _log_audit("submit_review", "DocumentRevision", revision.id, request, {"status": "in_review"})
        return Response(self.get_serializer(revision).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        revision = self.get_object()
        if revision.status not in ("draft", "in_review"):
            return Response(
                {"code": "invalid_status", "message": "Estado no permite aprobar."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        models.DocumentRevision.objects.filter(
            document=revision.document,
            status="approved",
        ).exclude(id=revision.id).update(status="archived")
        revision.status = "approved"
        revision.save(update_fields=["status"])
        revision.document.status = "active"
        revision.document.save(update_fields=["status"])
        _log_audit("approve", "DocumentRevision", revision.id, request, {"status": "approved"})
        return Response(self.get_serializer(revision).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        revision = self.get_object()
        if revision.status not in ("draft", "in_review"):
            return Response(
                {"code": "invalid_status", "message": "Estado no permite rechazar."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        revision.status = "rejected"
        revision.save(update_fields=["status"])
        revision.document.status = "archived"
        revision.document.save(update_fields=["status"])
        _log_audit("reject", "DocumentRevision", revision.id, request, {"status": "rejected"})
        return Response(self.get_serializer(revision).data)


class DocumentApprovalViewSet(BaseRoleViewSet):
    queryset = models.DocumentApproval.objects.all()
    serializer_class = serializers.DocumentApprovalSerializer
    write_roles = ["Admin", "Supervisor", "Inspector"]

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        approval = self.get_object()
        if approval.status != "pending":
            return Response(
                {"code": "invalid_status", "message": "Estado no permite aprobar."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        approval.status = "approved"
        approval.save(update_fields=["status"])
        _log_audit("approve", "DocumentApproval", approval.id, request, {"status": "approved"})
        return Response(self.get_serializer(approval).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        approval = self.get_object()
        if approval.status != "pending":
            return Response(
                {"code": "invalid_status", "message": "Estado no permite rechazar."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        approval.status = "rejected"
        approval.save(update_fields=["status"])
        _log_audit("reject", "DocumentApproval", approval.id, request, {"status": "rejected"})
        return Response(self.get_serializer(approval).data)


class DocumentSignatureViewSet(BaseRoleViewSet):
    queryset = models.DocumentSignature.objects.all()
    serializer_class = serializers.DocumentSignatureSerializer

