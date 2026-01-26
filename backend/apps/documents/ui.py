import os
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
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


@login_required
def document_list(request):
    q = request.GET.get("q")
    project_id = request.GET.get("project_id")
    items = models.Document.objects.select_related("project").all().order_by("title")
    if q:
        items = items.filter(title__icontains=q)
    if project_id:
        items = items.filter(project_id=project_id)
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
    return render(
        request,
        "documents/detail.html",
        {
            "item": item,
            "revisions": revisions,
            "approvals": approvals,
            "signatures": signatures,
        },
    )


@login_required
def document_create(request):
    if request.method == "POST":
        form = DocumentForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("document_detail", pk=item.pk)
    else:
        form = DocumentForm()
    return render(request, "documents/form.html", {"form": form, "title": "Nuevo documento"})


@login_required
def document_edit(request, pk):
    item = get_object_or_404(models.Document, pk=pk)
    if request.method == "POST":
        form = DocumentForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("document_detail", pk=item.pk)
    else:
        form = DocumentForm(instance=item)
    return render(request, "documents/form.html", {"form": form, "title": "Editar documento"})


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
        {"form": form, "title": "Nueva revision", "document": document},
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
        {"form": form, "title": "Nuevo aprobador", "revision": revision},
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
        {"form": form, "title": "Nueva firma", "revision": revision},
    )
