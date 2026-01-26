import json
from uuid import UUID

from django.utils.deprecation import MiddlewareMixin

from apps.projects import models as project_models
from apps.users import models as user_models


class AuditEventMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return response
        if not request.path.startswith("/api/"):
            return response

        email = getattr(request.user, "email", None) or getattr(request.user, "username", None)
        if not email:
            return response
        app_user = user_models.User.objects.filter(email=email).first()
        if not app_user:
            return response

        parts = [p for p in request.path.split("/") if p]
        entity = parts[1] if len(parts) > 1 else "api"
        entity_id = None
        for part in parts:
            try:
                entity_id = UUID(part)
                break
            except ValueError:
                continue

        payload = {
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "query": request.GET.dict(),
        }
        body = None
        if hasattr(request, "data"):
            try:
                body = request.data
            except Exception:
                body = None
        if body is None and request.body:
            try:
                body = json.loads(request.body.decode("utf-8"))
            except Exception:
                body = None
        if body is not None:
            payload["body"] = body

        project_models.AuditEvent.objects.create(
            event_code="api_write",
            entity=entity,
            entity_id=entity_id or app_user.id,
            user=app_user,
            payload_json=payload,
        )
        return response
