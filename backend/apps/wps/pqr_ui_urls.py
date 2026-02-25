from django.urls import path

from . import ui


urlpatterns = [
    path("", ui.pqr_list, name="pqr_list"),
    path("new/tool/", ui.pqr_create_tool, name="pqr_create_tool"),
    path("<uuid:pk>/", ui.pqr_detail, name="pqr_detail"),
    path("<uuid:pk>/edit/", ui.pqr_edit, name="pqr_edit"),
    path("<uuid:pk>/copy/", ui.pqr_copy, name="pqr_copy"),
    path("<uuid:pk>/delete/", ui.pqr_delete, name="pqr_delete"),
    path("<uuid:pk>/upload-scan/", ui.pqr_upload_scan, name="pqr_upload_scan"),
    path("<uuid:pk>/submit-review/", ui.pqr_submit_review, name="pqr_submit_review"),
    path("<uuid:pk>/approve/", ui.pqr_approve, name="pqr_approve"),
]
