import uuid
from django.db import models


class Drawing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    equipment = models.ForeignKey(
        "projects.ProjectEquipment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    code = models.CharField(max_length=100)
    revision = models.CharField(max_length=20)
    file_path = models.CharField(max_length=512)
    status = models.CharField(max_length=30, default="active")

    class Meta:
        db_table = "Drawing"
        constraints = [
            models.UniqueConstraint(fields=["project", "code", "revision"], name="drawing_project_code_rev_unique")
        ]

    def __str__(self):
        return f"{self.code}-R{self.revision}"


class WeldMap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    drawing = models.ForeignKey("welds.Drawing", on_delete=models.CASCADE)
    status = models.CharField(max_length=30, default="active")

    class Meta:
        db_table = "WeldMap"
        constraints = [
            models.UniqueConstraint(fields=["project", "drawing"], name="weldmap_project_drawing_unique")
        ]

    def __str__(self):
        return f"{self.project.code} / {self.drawing.code}-R{self.drawing.revision}"


class Weld(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    drawing = models.ForeignKey("welds.Drawing", on_delete=models.SET_NULL, null=True)
    number = models.CharField(max_length=100)
    status = models.CharField(max_length=30, default="planned")
    closed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "Weld"
        constraints = [
            models.UniqueConstraint(fields=["project", "number"], name="weld_project_number_unique")
        ]

    def __str__(self):
        return self.number


class WeldMark(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    weld_map = models.ForeignKey("welds.WeldMap", on_delete=models.CASCADE)
    weld = models.ForeignKey("welds.Weld", on_delete=models.CASCADE)
    geometry = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "WeldMark"


class WeldWpsAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    weld = models.ForeignKey("welds.Weld", on_delete=models.CASCADE)
    wps = models.ForeignKey("wps.Wps", on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=30, default="active")

    class Meta:
        db_table = "WeldWpsAssignment"


class WeldWelderAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    weld = models.ForeignKey("welds.Weld", on_delete=models.CASCADE)
    welder = models.ForeignKey("wpq.Welder", on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=30, default="active")

    class Meta:
        db_table = "WeldWelderAssignment"


class WeldAttribute(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    weld = models.ForeignKey("welds.Weld", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.TextField()

    class Meta:
        db_table = "WeldAttribute"


class WeldAttributeCatalog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=20, default="text")
    enum_values = models.JSONField(blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=30, default="active")

    class Meta:
        db_table = "WeldAttributeCatalog"


class WeldMaterial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    weld = models.ForeignKey("welds.Weld", on_delete=models.CASCADE)
    material = models.ForeignKey("wps.MaterialBase", on_delete=models.CASCADE)
    heat_number = models.CharField(max_length=50)

    class Meta:
        db_table = "WeldMaterial"


class WeldConsumable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    weld = models.ForeignKey("welds.Weld", on_delete=models.CASCADE)
    consumable = models.ForeignKey("wps.FillerMaterial", on_delete=models.CASCADE)
    batch = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "WeldConsumable"


class VisualInspection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    weld = models.ForeignKey("welds.Weld", on_delete=models.CASCADE)
    stage = models.CharField(max_length=20)
    result = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)
    inspector = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "VisualInspection"


class WorkPack(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    status = models.CharField(max_length=30, default="open")

    class Meta:
        db_table = "WorkPack"


class Traveler(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_pack = models.ForeignKey("welds.WorkPack", on_delete=models.CASCADE)
    file_path = models.CharField(max_length=512, blank=True, null=True)
    status = models.CharField(max_length=30, default="draft")

    class Meta:
        db_table = "Traveler"
