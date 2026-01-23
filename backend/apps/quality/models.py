import uuid
from django.db import models


class ValidationRuleSet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    applies_to = models.CharField(max_length=10)
    standard = models.CharField(max_length=30)
    status = models.CharField(max_length=30, default="active")

    class Meta:
        db_table = "ValidationRuleSet"


class ValidationRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    applies_to = models.CharField(max_length=10)
    severity = models.CharField(max_length=20, default="error")
    rule_json = models.JSONField()
    status = models.CharField(max_length=30, default="active")

    class Meta:
        db_table = "ValidationRule"


class ValidationRuleSetItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ruleset = models.ForeignKey("quality.ValidationRuleSet", on_delete=models.CASCADE)
    rule = models.ForeignKey("quality.ValidationRule", on_delete=models.CASCADE)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "ValidationRuleSetItem"
        constraints = [
            models.UniqueConstraint(fields=["ruleset", "rule"], name="ruleset_rule_unique")
        ]


class NdeRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    weld = models.ForeignKey("welds.Weld", on_delete=models.SET_NULL, null=True)
    method = models.CharField(max_length=10)
    status = models.CharField(max_length=30, default="requested")
    requested_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "NdeRequest"


class NdeResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nde_request = models.ForeignKey("quality.NdeRequest", on_delete=models.CASCADE)
    result = models.CharField(max_length=20)
    defect_type = models.CharField(max_length=50, blank=True, null=True)
    report_path = models.CharField(max_length=512, blank=True, null=True)
    inspector = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "NdeResult"


class PwhtRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    weld = models.ForeignKey("welds.Weld", on_delete=models.CASCADE)
    cycle_params_json = models.JSONField(default=dict)
    result = models.CharField(max_length=20)
    report_path = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        db_table = "PwhtRecord"


class PressureTest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    line_id = models.CharField(max_length=100)
    test_type = models.CharField(max_length=20)
    pressure = models.DecimalField(max_digits=12, decimal_places=3, blank=True, null=True)
    duration_min = models.IntegerField(blank=True, null=True)
    result = models.CharField(max_length=20)
    report_path = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        db_table = "PressureTest"


class NdeSamplingRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    method = models.CharField(max_length=10)
    ratio = models.DecimalField(max_digits=12, decimal_places=3)
    penalty_json = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "NdeSamplingRule"
