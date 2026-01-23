import hashlib
import hmac
import json
import urllib.request

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from . import models
from . import serializers
from apps.users.permissions import RolePermission

class BaseRoleViewSet(viewsets.ModelViewSet):
    permission_classes = [RolePermission]
    read_roles = ["Admin"]
    write_roles = ["Admin"]


class IntegrationEndpointViewSet(BaseRoleViewSet):
    queryset = models.IntegrationEndpoint.objects.all()
    serializer_class = serializers.IntegrationEndpointSerializer

    @action(detail=True, methods=["post"], url_path="test-event")
    def test_event(self, request, pk=None):
        integration = self.get_object()
        payload = request.data.get("payload", {"event": "test"})
        event = models.IntegrationEvent.objects.create(
            integration=integration,
            event_type="test",
            payload_json=payload,
            status="queued",
        )
        return Response(
            serializers.IntegrationEventSerializer(event).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="test-delivery")
    def test_delivery(self, request, pk=None):
        integration = self.get_object()
        payload = request.data.get("payload", {"event": "test"})
        event = models.IntegrationEvent(
            integration=integration,
            event_type="test",
            payload_json=payload,
            status="queued",
        )
        try:
            IntegrationEventViewSet()._deliver_event(event)
        except Exception as exc:
            return Response(
                {"code": "delivery_failed", "message": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({"status": "ok"})


class IntegrationEventViewSet(BaseRoleViewSet):
    queryset = models.IntegrationEvent.objects.all()
    serializer_class = serializers.IntegrationEventSerializer

    def _deliver_event(self, event):
        payload = json.dumps(event.payload_json).encode("utf-8")
        secret = (event.integration.auth_json or {}).get("secret", "")
        signature = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        req = urllib.request.Request(
            event.integration.url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Event-Type": event.event_type,
                "X-Signature": signature,
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status >= 400:
                raise RuntimeError(f"HTTP {resp.status}")

    @action(detail=True, methods=["post"], url_path="deliver")
    def deliver(self, request, pk=None):
        event = self.get_object()
        try:
            self._deliver_event(event)
            event.status = "sent"
            event.delivered_at = timezone.now()
            event.save(update_fields=["status", "delivered_at"])
        except Exception as exc:
            event.status = "failed"
            event.attempts = event.attempts + 1
            event.last_error = str(exc)
            event.save(update_fields=["status", "attempts", "last_error"])
            return Response(
                {"code": "delivery_failed", "message": "Webhook fallo."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(self.get_serializer(event).data)

    @action(detail=False, methods=["post"], url_path="deliver-queue")
    def deliver_queue(self, request):
        pending = models.IntegrationEvent.objects.filter(status="queued").order_by("created_at")[:50]
        delivered = 0
        failed = 0
        for event in pending:
            try:
                self._deliver_event(event)
                event.status = "sent"
                event.delivered_at = timezone.now()
                event.save(update_fields=["status", "delivered_at"])
                delivered += 1
            except Exception as exc:
                event.status = "failed"
                event.attempts = event.attempts + 1
                event.last_error = str(exc)
                event.save(update_fields=["status", "attempts", "last_error"])
                failed += 1
        return Response({"delivered": delivered, "failed": failed})

