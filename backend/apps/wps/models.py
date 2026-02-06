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
    STATUS_DRAFT = "draft"
    STATUS_PENDING_APPROVAL = "pending_approval"
    STATUS_REVIEWED = "reviewed"
    STATUS_APPROVED = "approved"
    STATUS_ARCHIVED = "archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.SET_NULL, null=True)
    equipment = models.ForeignKey(
        "projects.ProjectEquipment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    code = models.CharField(max_length=100)
    standard = models.CharField(max_length=30)
    impact_test = models.BooleanField(default=False)
    status = models.CharField(max_length=30, default="draft")
    root_wps = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revisions",
    )
    revision_number = models.IntegerField(default=0)
    is_current = models.BooleanField(default=True)
    submitted_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wps_submitted_set",
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wps_reviewed_set",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wps_approved_set",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "Wps"
        constraints = [
            models.UniqueConstraint(
                fields=["project", "code", "revision_number"],
                name="wps_project_code_revision_unique",
            )
        ]


class Pqr(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=100)
    standard = models.CharField(max_length=30)
    status = models.CharField(max_length=30, default="draft")
    scanned_pdf = models.FileField(upload_to="pqr_scans/", blank=True, null=True)

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


class WpsProcess(models.Model):
    PROCESS_CHOICES = (
        ("SMAW", "SMAW"),
        ("GTAW", "GTAW"),
        ("GMAW", "GMAW"),
        ("FCAW", "FCAW"),
    )
    SPECIAL_CHOICES = (
        ("HFO", "HFO"),
        ("CRO", "CRO"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wps = models.ForeignKey("wps.Wps", on_delete=models.CASCADE)
    process_code = models.CharField(max_length=20, choices=PROCESS_CHOICES)
    special_process = models.CharField(
        max_length=10, choices=SPECIAL_CHOICES, blank=True, null=True
    )
    order = models.IntegerField(default=1)

    class Meta:
        db_table = "WpsProcess"
        constraints = [
            models.UniqueConstraint(fields=["wps", "process_code"], name="wps_process_unique")
        ]


class WpsVariableDefinition(models.Model):
    CATEGORY_CHOICES = (
        ("essential", "Essential"),
        ("supplementary", "Supplementary Essential"),
        ("nonessential", "Nonessential"),
    )
    DATA_TYPE_CHOICES = (
        ("text", "Text"),
        ("number", "Number"),
        ("enum", "Enum"),
        ("boolean", "Boolean"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    process_code = models.CharField(max_length=20)
    special_process = models.CharField(max_length=10, blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES, default="text")
    unit = models.CharField(max_length=20, blank=True, null=True)
    options_json = models.JSONField(blank=True, null=True)
    change_note = models.CharField(max_length=100, blank=True, null=True)
    paragraph = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "WpsVariableDefinition"
        constraints = [
            models.UniqueConstraint(
                fields=["process_code", "special_process", "code"],
                name="wps_var_def_unique",
            )
        ]


class WpsVariableValue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wps_process = models.ForeignKey("wps.WpsProcess", on_delete=models.CASCADE)
    definition = models.ForeignKey("wps.WpsVariableDefinition", on_delete=models.CASCADE)
    value = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = "WpsVariableValue"
        constraints = [
            models.UniqueConstraint(
                fields=["wps_process", "definition"],
                name="wps_var_value_unique",
            )
        ]


class PqrResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pqr = models.ForeignKey("wps.Pqr", on_delete=models.CASCADE)
    test_type = models.CharField(max_length=50)
    result = models.TextField()
    report_path = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        db_table = "PqrResult"
