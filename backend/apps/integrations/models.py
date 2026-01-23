import uuid
from django.db import models


class IntegrationEndpoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=2048)
    status = models.CharField(max_length=30, default="active")
    auth_json = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "IntegrationEndpoint"


class IntegrationEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey("integrations.IntegrationEndpoint", on_delete=models.CASCADE)
    event_type = models.CharField(max_length=100)
    payload_json = models.JSONField()
    status = models.CharField(max_length=30, default="queued")
    attempts = models.IntegerField(default=0)
    last_error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "IntegrationEvent"
