import uuid
from django.db import models


class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    type = models.CharField(max_length=30)
    params_json = models.JSONField(default=dict)
    file_path = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        db_table = "Report"


class Dossier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    config_json = models.JSONField(default=dict)
    file_path = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        db_table = "Dossier"


class ImportJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20)
    status = models.CharField(max_length=30, default="queued")
    created_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    file_path = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ImportJob"


class ImportError(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey("reports.ImportJob", on_delete=models.CASCADE)
    row_number = models.IntegerField()
    message = models.TextField()

    class Meta:
        db_table = "ImportError"
