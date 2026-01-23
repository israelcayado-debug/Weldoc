from django.test import TestCase
from rest_framework.test import APIClient

from apps.users import models as user_models
from apps.projects import models as project_models
from . import models


class IntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.app_user = user_models.User.objects.create(
            name="admin", email="admin@example.local", status="active"
        )
        role, _ = user_models.Role.objects.get_or_create(name="Admin", defaults={"scope": "global"})
        user_models.UserRole.objects.get_or_create(user=self.app_user, role=role)
        self.project = project_models.Project.objects.create(
            name="P1", code="P1", units="metric", status="active", standard_set=["ASME_IX"]
        )
        project_models.ProjectUser.objects.create(
            project=self.project, user=self.app_user, role=role
        )
        self.client.force_authenticate(user=self._auth_user())

    def _auth_user(self):
        from django.contrib.auth import get_user_model

        AuthUser = get_user_model()
        auth_user, _ = AuthUser.objects.get_or_create(
            username="admin", defaults={"email": self.app_user.email}
        )
        return auth_user

    def test_create_integration_event(self):
        integration = models.IntegrationEndpoint.objects.create(
            name="Local", url="http://example.local", status="active", auth_json={"secret": "x"}
        )
        resp = self.client.post(
            f"/api/integrations/{integration.id}/test-event/",
            {"payload": {"event": "test"}},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
