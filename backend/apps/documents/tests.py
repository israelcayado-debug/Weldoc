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
            project=None, code="PQR-1", standard="ASME_IX", status="approved"
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


    def test_detail_shows_equipment_scope_and_global_pqr(self):
        project = project_models.Project.objects.create(
            name="Project Scope",
            code="00000013",
            units="metric",
            status="active",
            standard_set=["ASME_IX"],
        )
        eq1 = project_models.ProjectEquipment.objects.create(
            project=project, name="Vessel A", fabrication_code="EQ-A", status="active"
        )
        eq2 = project_models.ProjectEquipment.objects.create(
            project=project, name="Vessel B", fabrication_code="EQ-B", status="active"
        )
        drawing1 = weld_models.Drawing.objects.create(
            project=project,
            equipment=eq1,
            code="D-A",
            revision="0",
            file_path="drawings/da.pdf",
            status="active",
        )
        drawing2 = weld_models.Drawing.objects.create(
            project=project,
            equipment=eq2,
            code="D-B",
            revision="0",
            file_path="drawings/db.pdf",
            status="active",
        )
        weld_models.WeldMap.objects.create(project=project, drawing=drawing1)
        weld_models.WeldMap.objects.create(project=project, drawing=drawing2)
        weld_models.Weld.objects.create(project=project, drawing=drawing1, number="W-A")
        weld_models.Weld.objects.create(project=project, drawing=drawing2, number="W-B")
        wps_models.Wps.objects.create(
            project=project, equipment=eq1, code="WPS-A", standard="ASME_IX", status="draft"
        )
        wps_models.Wps.objects.create(
            project=project, equipment=eq2, code="WPS-B", standard="ASME_IX", status="draft"
        )
        wps_models.Pqr.objects.create(project=None, code="PQR-GLOBAL", standard="ASME_IX", status="approved")

        book = models.Document.objects.create(
            project=project,
            equipment=eq1,
            type="Welding Book",
            title="WB Scope",
            status="active",
        )

        response = self.client.get(reverse("document_detail", args=[book.id]))
        self.assertEqual(response.status_code, 200)
        composition = response.context["composition"]
        self.assertEqual(composition["welding_map_count"], 1)
        self.assertEqual(composition["welding_list_count"], 1)
        self.assertEqual(composition["wps_count"], 1)
        self.assertEqual(composition["pqr_count"], 1)

    def test_document_copy_creates_new_welding_book(self):
        project = project_models.Project.objects.create(
            name="Project Copy",
            code="00000011",
            units="metric",
            status="active",
            standard_set=["ASME_IX"],
        )
        source = models.Document.objects.create(
            project=project,
            type="Welding Book",
            title="WB Source",
            status="active",
        )

        response = self.client.post(reverse("document_copy", args=[source.id]))
        self.assertEqual(response.status_code, 302)

        copied = models.Document.objects.get(title="WB Source (Copy)")
        self.assertEqual(copied.project_id, source.project_id)
        self.assertEqual(copied.type, "Welding Book")

    def test_document_delete_removes_welding_book(self):
        project = project_models.Project.objects.create(
            name="Project Delete",
            code="00000012",
            units="metric",
            status="active",
            standard_set=["ASME_IX"],
        )
        item = models.Document.objects.create(
            project=project,
            type="Welding Book",
            title="WB Delete",
            status="active",
        )

        response = self.client.post(reverse("document_delete", args=[item.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(models.Document.objects.filter(id=item.id).exists())
