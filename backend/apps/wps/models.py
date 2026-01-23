import uuid
from django.db import models


class MaterialBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spec = models.CharField(max_length=100)
    grade = models.CharField(max_length=100, blank=True, null=True)
    group_no = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "MaterialBase"


class FillerMaterial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spec = models.CharField(max_length=100)
    classification = models.CharField(max_length=100, blank=True, null=True)
    group_no = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "FillerMaterial"


class JointType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    geometry_json = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "JointType"


class Wps(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=100)
    standard = models.CharField(max_length=30)
    status = models.CharField(max_length=30, default="draft")

    class Meta:
        db_table = "Wps"
        constraints = [
            models.UniqueConstraint(fields=["project", "code"], name="wps_project_code_unique")
        ]


class Pqr(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=100)
    standard = models.CharField(max_length=30)
    status = models.CharField(max_length=30, default="draft")

    class Meta:
        db_table = "Pqr"
        constraints = [
            models.UniqueConstraint(fields=["project", "code"], name="pqr_project_code_unique")
        ]


class WpsPqrLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wps = models.ForeignKey("wps.Wps", on_delete=models.CASCADE)
    pqr = models.ForeignKey("wps.Pqr", on_delete=models.CASCADE)

    class Meta:
        db_table = "WpsPqrLink"
        constraints = [
            models.UniqueConstraint(fields=["wps", "pqr"], name="wps_pqr_unique")
        ]


class WpsVariable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wps = models.ForeignKey("wps.Wps", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.TextField()
    unit = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = "WpsVariable"


class PqrResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pqr = models.ForeignKey("wps.Pqr", on_delete=models.CASCADE)
    test_type = models.CharField(max_length=50)
    result = models.TextField()
    report_path = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        db_table = "PqrResult"
