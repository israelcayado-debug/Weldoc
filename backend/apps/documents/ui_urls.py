from django.urls import path

from . import ui


urlpatterns = [
    path("", ui.document_list, name="document_list"),
    path("new/", ui.document_create, name="document_create"),
    path("<uuid:pk>/", ui.document_detail, name="document_detail"),
    path("<uuid:pk>/edit/", ui.document_edit, name="document_edit"),
    path("<uuid:pk>/copy/", ui.document_copy, name="document_copy"),
    path("<uuid:pk>/delete/", ui.document_delete, name="document_delete"),
    path("<uuid:pk>/revisions/new/", ui.document_revision_create, name="document_revision_create"),
    path("revisions/<uuid:pk>/submit/", ui.document_revision_submit, name="document_revision_submit"),
    path("revisions/<uuid:pk>/approve/", ui.document_revision_approve, name="document_revision_approve"),
    path("revisions/<uuid:pk>/reject/", ui.document_revision_reject, name="document_revision_reject"),
    path("revisions/<uuid:pk>/approvals/new/", ui.document_approval_create, name="document_approval_create"),
    path("approvals/<uuid:pk>/approve/", ui.document_approval_approve, name="document_approval_approve"),
    path("approvals/<uuid:pk>/reject/", ui.document_approval_reject, name="document_approval_reject"),
    path("revisions/<uuid:pk>/signatures/new/", ui.document_signature_create, name="document_signature_create"),
]
