import uuid
from django.db import models


class SchemaVersion(models.Model):
    version = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "SchemaVersion"


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=30, default="active")

    class Meta:
        db_table = "Client"


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey("projects.Client", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=100, unique=True)
    purchase_order = models.CharField(max_length=100, blank=True, null=True)
    units = models.CharField(max_length=20, default="metric")
    status = models.CharField(max_length=30, default="active")
    standard_set = models.JSONField(default=list)

    class Meta:
        db_table = "Project"


class ProjectEquipment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    fabrication_code = models.CharField(max_length=100)
    status = models.CharField(max_length=30, default="active")

    class Meta:
        db_table = "ProjectEquipment"
        constraints = [
            models.UniqueConstraint(
                fields=["project", "fabrication_code"],
                name="project_equipment_fabrication_unique",
            )
        ]

class ProjectUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    role = models.ForeignKey("users.Role", on_delete=models.CASCADE)

    class Meta:
        db_table = "ProjectUser"
        constraints = [
            models.UniqueConstraint(fields=["project", "user", "role"], name="project_user_role_unique")
        ]


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity = models.CharField(max_length=50)
    entity_id = models.UUIDField()
    action = models.CharField(max_length=50)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    at = models.DateTimeField(auto_now_add=True)
    diff_json = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "AuditLog"


class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_code = models.CharField(max_length=100)
    entity = models.CharField(max_length=50)
    entity_id = models.UUIDField()
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    at = models.DateTimeField(auto_now_add=True)
    payload_json = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "AuditEvent"


class NumberingRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    type = models.CharField(max_length=20)
    pattern = models.CharField(max_length=200)
    next_seq = models.IntegerField(default=1)

    class Meta:
        db_table = "NumberingRule"
