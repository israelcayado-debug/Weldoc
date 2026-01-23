from django.test import TestCase
from rest_framework.test import APIClient

from apps.users import models as user_models
from apps.projects import models as project_models
from . import models


class ContinuityRecalculateTests(TestCase):
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

    def test_recalculate_no_activity(self):
        welder = models.Welder.objects.create(name="W1", status="active")
        resp = self.client.post(f"/api/welders/{welder.id}/continuity-recalculate/")
        self.assertEqual(resp.status_code, 200)
