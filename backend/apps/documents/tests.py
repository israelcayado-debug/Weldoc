from django.test import TestCase
from django.urls import reverse

from apps.projects import models as project_models
from apps.welds import models as weld_models
from apps.wps import models as wps_models
from . import models


class WeldingBookUiTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        AuthUser = get_user_model()
        self.user = AuthUser.objects.create_user(username="documents-ui", password="12345")
        self.client.login(username="documents-ui", password="12345")

    def test_list_shows_only_welding_books_with_project_counts(self):
        project = project_models.Project.objects.create(
            name="Project One",
            code="00000001",
            purchase_order="PO-1",
            units="metric",
            status="active",
            standard_set=["ASME_IX"],
        )

        book = models.Document.objects.create(
            project=project,
            type="Welding Book",
            title="WB-1",
            status="active",
        )
        models.Document.objects.create(
            project=project,
            type="General",
            title="General document",
            status="active",
        )

        drawing = weld_models.Drawing.objects.create(
            project=project,
            code="D-1",
            revision="0",
            file_path="drawings/d1.pdf",
            status="active",
        )
        weld_models.WeldMap.objects.create(project=project, drawing=drawing)
        weld_models.Weld.objects.create(project=project, number="W-1")
        wps_models.Wps.objects.create(
            project=project, code="WPS-1", standard="ASME_IX", status="draft"
        )
        wps_models.Pqr.objects.create(
            project=project, code="PQR-1", standard="ASME_IX", status="draft"
        )

        response = self.client.get(reverse("document_list"))
        self.assertEqual(response.status_code, 200)
        items = list(response.context["items"])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, book.id)
        self.assertEqual(items[0].welding_map_count, 1)
        self.assertEqual(items[0].welding_list_count, 1)
        self.assertEqual(items[0].wps_count, 1)
        self.assertEqual(items[0].pqr_count, 1)
