from django.contrib import admin
from . import models


@admin.register(models.Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "project", "status")
    search_fields = ("title",)


@admin.register(models.DocumentRevision)
class DocumentRevisionAdmin(admin.ModelAdmin):
    list_display = ("document", "revision", "status", "created_at")


@admin.register(models.DocumentApproval)
class DocumentApprovalAdmin(admin.ModelAdmin):
    list_display = ("document_revision", "approver", "status", "signed_at")


@admin.register(models.DocumentSignature)
class DocumentSignatureAdmin(admin.ModelAdmin):
    list_display = ("document_revision", "signer", "signed_at")
