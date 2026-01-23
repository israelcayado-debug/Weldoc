import uuid
from django.db import models


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=30, default="active")

    class Meta:
        db_table = "Document"


class DocumentRevision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey("documents.Document", on_delete=models.CASCADE)
    revision = models.CharField(max_length=20)
    file_path = models.CharField(max_length=512)
    status = models.CharField(max_length=30, default="draft")
    created_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "DocumentRevision"


class DocumentApproval(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_revision = models.ForeignKey("documents.DocumentRevision", on_delete=models.CASCADE)
    approver = models.ForeignKey("users.User", on_delete=models.CASCADE)
    status = models.CharField(max_length=30, default="pending")
    signed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "DocumentApproval"


class DocumentSignature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_revision = models.ForeignKey("documents.DocumentRevision", on_delete=models.CASCADE)
    signer = models.ForeignKey("users.User", on_delete=models.CASCADE)
    signature_blob = models.BinaryField()
    signed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "DocumentSignature"
