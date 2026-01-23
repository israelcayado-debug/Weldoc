import uuid
from django.db import models


class Welder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    employer = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=30, default="active")

    class Meta:
        db_table = "Welder"


class Wpq(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    welder = models.ForeignKey("wpq.Welder", on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    standard = models.CharField(max_length=30)
    status = models.CharField(max_length=30, default="draft")

    class Meta:
        db_table = "Wpq"
        constraints = [
            models.UniqueConstraint(fields=["welder", "code"], name="wpq_welder_code_unique")
        ]


class WpqProcess(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wpq = models.ForeignKey("wpq.Wpq", on_delete=models.CASCADE)
    process = models.CharField(max_length=30)
    positions = models.CharField(max_length=100, blank=True, null=True)
    thickness_range = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "WpqProcess"


class WpqTest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wpq = models.ForeignKey("wpq.Wpq", on_delete=models.CASCADE)
    test_type = models.CharField(max_length=50)
    result = models.TextField()
    report_path = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        db_table = "WpqTest"


class ContinuityLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    welder = models.ForeignKey("wpq.Welder", on_delete=models.CASCADE)
    weld = models.ForeignKey("welds.Weld", on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    process = models.CharField(max_length=30)

    class Meta:
        db_table = "ContinuityLog"


class ExpiryAlert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    welder = models.ForeignKey("wpq.Welder", on_delete=models.CASCADE)
    wpq = models.ForeignKey("wpq.Wpq", on_delete=models.CASCADE)
    due_date = models.DateField()
    sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "ExpiryAlert"


class WelderContinuity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    welder = models.OneToOneField("wpq.Welder", on_delete=models.CASCADE)
    last_activity_date = models.DateField(blank=True, null=True)
    continuity_due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=30, default="in_continuity")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "WelderContinuity"
