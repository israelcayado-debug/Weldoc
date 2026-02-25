import os
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from . import models
from .forms import (
    DocumentApprovalForm,
    DocumentForm,
    DocumentRevisionForm,
    DocumentSignatureForm,
)
from apps.projects import models as project_models
from apps.users import models as user_models
from apps.wps import models as wps_models
from apps.welds import models as weld_models


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


def _missing_wps_for_publish(document):
    qs = wps_models.Wps.objects.filter(
        project=document.project,
        is_current=True,
    )
    if document.equipment_id:
        qs = qs.filter(equipment_id=document.equipment_id)
    return list(qs.exclude(status=wps_models.Wps.STATUS_APPROVED).order_by("code"))




def _book_composition(document):
    welding_map_count = (
        weld_models.WeldMap.objects.filter(
            project=document.project,
            drawing__equipment_id=document.equipment_id,
        ).count()
        if document.equipment_id
        else weld_models.WeldMap.objects.filter(project=document.project).count()
    )
    weld_scope = weld_models.Weld.objects.filter(project=document.project)
    if document.equipment_id:
        weld_scope = weld_scope.filter(drawing__equipment_id=document.equipment_id)
    welding_list_count = weld_scope.count()
    wps_scope = wps_models.Wps.objects.filter(project=document.project, is_current=True)
    if document.equipment_id:
        wps_scope = wps_scope.filter(equipment_id=document.equipment_id)
    wps_count = wps_scope.count()
    pqr_count = wps_models.Pqr.objects.filter(standard="ASME_IX", status="approved").count()
    return {
        "welding_map_count": welding_map_count,
        "welding_list_count": welding_list_count,
        "wps_count": wps_count,
        "pqr_count": pqr_count,
    }


def _copy_title(source_title):
    for index in range(1, 1000):
        suffix = " (Copy)" if index == 1 else f" (Copy {index})"
        trimmed_base = source_title[: max(1, 200 - len(suffix))]
        candidate = f"{trimmed_base}{suffix}"
        if not models.Document.objects.filter(title=candidate).exists():
            return candidate
    return f"{source_title[:188]} (Copy 999)"


@login_required
def document_list(request):
    q = request.GET.get("q")
    project_id = request.GET.get("project_id")
    equipment_id = request.GET.get("equipment_id")
    welding_book_filter = (
        Q(type__iexact="welding book")
        | Q(type__iexact="welding_book")
        | Q(type__iexact="weldingbook")
        | Q(title__icontains="welding book")
    )
    items = list(
        models.Document.objects.select_related("project", "equipment")
        .filter(welding_book_filter)
        .order_by("project__code", "title")
    )
    if q:
        q_lower = q.lower()
        items = [
            item
            for item in items
            if q_lower in (item.title or "").lower()
            or q_lower in (item.project.name or "").lower()
            or q_lower in (item.project.code or "").lower()
        ]
    if project_id:
        items = [item for item in items if str(item.project_id) == project_id]
    if equipment_id:
        items = [item for item in items if str(item.equipment_id) == equipment_id]
    for item in items:
        composition = _book_composition(item)
        item.welding_map_count = composition["welding_map_count"]
        item.welding_list_count = composition["welding_list_count"]
        item.wps_count = composition["wps_count"]
        item.pqr_count = composition["pqr_count"]
    return render(request, "documents/list.html", {"items": items})


@login_required
def document_detail(request, pk):
    item = get_object_or_404(models.Document, pk=pk)
    revisions = models.DocumentRevision.objects.filter(document=item).order_by("-created_at")
    approvals = models.DocumentApproval.objects.filter(
        document_revision__document=item
    ).select_related("approver", "document_revision")
    signatures = models.DocumentSignature.objects.filter(
        document_revision__document=item
    ).select_related("signer", "document_revision")
    publish_error = request.GET.get("publish_error")
    missing_wps = request.GET.get("missing_wps", "")
    composition = _book_composition(item)
    return render(
        request,
        "documents/detail.html",
        {
            "item": item,
            "revisions": revisions,
            "approvals": approvals,
            "signatures": signatures,
            "publish_error": publish_error,
            "missing_wps": missing_wps,
            "composition": composition,
        },
    )


@login_required
def document_create(request):
    if request.method == "POST":
        form = DocumentForm(request.POST)
        form.fields.pop("type", None)
        if form.is_valid():
            item = form.save(commit=False)
            item.type = "Welding Book"
            item.save()
            return redirect("document_detail", pk=item.pk)
    else:
        form = DocumentForm()
        form.fields.pop("type", None)
    return render(request, "documents/form.html", {"form": form, "title": "New Welding Book"})


@login_required
def document_edit(request, pk):
    item = get_object_or_404(models.Document, pk=pk)
    if request.method == "POST":
        form = DocumentForm(request.POST, instance=item)
        form.fields.pop("type", None)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.type = "Welding Book"
            updated.save()
            return redirect("document_detail", pk=item.pk)
    else:
        form = DocumentForm(instance=item)
        form.fields.pop("type", None)
    return render(request, "documents/form.html", {"form": form, "title": "Edit Welding Book"})


@login_required
def document_copy(request, pk):
    if request.method != "POST":
        return redirect("document_list")

    source = get_object_or_404(models.Document, pk=pk)
    copy_item = models.Document.objects.create(
        project=source.project,
        equipment=source.equipment,
        type="Welding Book",
        title=_copy_title(source.title),
        status=source.status,
    )
    return redirect("document_detail", pk=copy_item.pk)


@login_required
def document_delete(request, pk):
    if request.method == "POST":
        item = get_object_or_404(models.Document, pk=pk)
        item.delete()
    return redirect("document_list")


@login_required
def document_revision_create(request, pk):
    document = get_object_or_404(models.Document, pk=pk)
    if request.method == "POST":
        form = DocumentRevisionForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.document = document
            upload = form.cleaned_data.get("upload")
            if upload:
                filename = f"{uuid.uuid4().hex}_{upload.name}"
                rel_path = os.path.join("documents", filename)
                abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "wb") as handle:
                    for chunk in upload.chunks():
                        handle.write(chunk)
                item.file_path = rel_path
            else:
                item.file_path = ""
            item.status = "draft"
            item.save()
            return redirect("document_detail", pk=document.pk)
    else:
        form = DocumentRevisionForm(
            initial={"document": document.id, "status": "draft"}
        )
    return render(
        request,
        "documents/revision_form.html",
        {"form": form, "title": "New revision", "document": document},
    )


@login_required
def document_revision_submit(request, pk):
    revision = get_object_or_404(models.DocumentRevision, pk=pk)
    if revision.status == "draft":
        revision.status = "in_review"
        revision.save(update_fields=["status"])
        _log_audit("submit_review", "DocumentRevision", revision.id, request, {"status": "in_review"})
    return redirect("document_detail", pk=revision.document_id)


@login_required
def document_revision_approve(request, pk):
    revision = get_object_or_404(models.DocumentRevision, pk=pk)
    if revision.status in ("draft", "in_review"):
        missing_wps = _missing_wps_for_publish(revision.document)
        if missing_wps:
            missing_codes = ",".join([wps.code for wps in missing_wps])
            return redirect(
                f"/ui/documents/{revision.document_id}/?publish_error=wps_not_approved&missing_wps={missing_codes}"
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
    return redirect("document_detail", pk=revision.document_id)


@login_required
def document_revision_reject(request, pk):
    revision = get_object_or_404(models.DocumentRevision, pk=pk)
    if revision.status in ("draft", "in_review"):
        revision.status = "rejected"
        revision.save(update_fields=["status"])
        revision.document.status = "archived"
        revision.document.save(update_fields=["status"])
        _log_audit("reject", "DocumentRevision", revision.id, request, {"status": "rejected"})
    return redirect("document_detail", pk=revision.document_id)


@login_required
def document_approval_create(request, pk):
    revision = get_object_or_404(models.DocumentRevision, pk=pk)
    if request.method == "POST":
        form = DocumentApprovalForm(request.POST)
        if form.is_valid():
            approval = form.save(commit=False)
            approval.document_revision = revision
            approval.status = "pending"
            approval.save()
            return redirect("document_detail", pk=revision.document_id)
    else:
        form = DocumentApprovalForm(initial={"document_revision": revision.id, "status": "pending"})
    return render(
        request,
        "documents/approval_form.html",
        {"form": form, "title": "New approver", "revision": revision},
    )


@login_required
def document_approval_approve(request, pk):
    approval = get_object_or_404(models.DocumentApproval, pk=pk)
    if approval.status == "pending":
        approval.status = "approved"
        approval.save(update_fields=["status"])
        _log_audit("approve", "DocumentApproval", approval.id, request, {"status": "approved"})
    return redirect("document_detail", pk=approval.document_revision.document_id)


@login_required
def document_approval_reject(request, pk):
    approval = get_object_or_404(models.DocumentApproval, pk=pk)
    if approval.status == "pending":
        approval.status = "rejected"
        approval.save(update_fields=["status"])
        _log_audit("reject", "DocumentApproval", approval.id, request, {"status": "rejected"})
    return redirect("document_detail", pk=approval.document_revision.document_id)


@login_required
def document_signature_create(request, pk):
    revision = get_object_or_404(models.DocumentRevision, pk=pk)
    if request.method == "POST":
        form = DocumentSignatureForm(request.POST)
        if form.is_valid():
            signature = form.save(commit=False)
            signature.document_revision = revision
            signature.save()
            return redirect("document_detail", pk=revision.document_id)
    else:
        form = DocumentSignatureForm(initial={"document_revision": revision.id})
    return render(
        request,
        "documents/signature_form.html",
        {"form": form, "title": "New signature", "revision": revision},
    )
