from django.test import TestCase
from django.urls import reverse

from apps.documents import models as document_models
from apps.welds import models as weld_models
from apps.wpq import models as wpq_models
from apps.wps import models as wps_models
from . import models


class ProjectListUiTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        AuthUser = get_user_model()
        self.user = AuthUser.objects.create_user(username="project-ui", password="12345")
        self.client.login(username="project-ui", password="12345")

    def test_project_list_includes_summary_columns(self):
        project = models.Project.objects.create(
            name="Project One",
            code="00000001",
            purchase_order="PO-1",
            units="metric",
            status="active",
            standard_set=["ASME_IX"],
        )

        document_models.Document.objects.create(
            project=project,
            type="Welding Book",
            title="WB-1",
            status="active",
        )
        wps_models.Wps.objects.create(
            project=project,
            code="WPS-1",
            standard="ASME_IX",
            status="draft",
        )
        wps_models.Pqr.objects.create(
            project=project,
            code="PQR-1",
            standard="ASME_IX",
            status="draft",
        )
        weld = weld_models.Weld.objects.create(project=project, number="W-1")
        welder = wpq_models.Welder.objects.create(name="Welder A")
        weld_models.WeldWelderAssignment.objects.create(weld=weld, welder=welder)

        response = self.client.get(reverse("project_list"))
        self.assertEqual(response.status_code, 200)
        item = response.context["items"].get(id=project.id)
        self.assertEqual(item.welding_book_count, 1)
        self.assertEqual(item.wps_count, 1)
        self.assertEqual(item.pqr_count, 1)
        self.assertEqual(item.welder_count, 1)


    def test_project_detail_shows_welder_wpq_status(self):
        project = models.Project.objects.create(
            name="Project Qualification",
            code="00000040",
            units="metric",
            status="active",
            standard_set=["ASME_IX"],
        )
        weld = weld_models.Weld.objects.create(project=project, number="W-40")
        welder_ok = wpq_models.Welder.objects.create(name="Welder OK")
        welder_no = wpq_models.Welder.objects.create(name="Welder NO")
        weld_models.WeldWelderAssignment.objects.create(weld=weld, welder=welder_ok)
        weld_models.WeldWelderAssignment.objects.create(weld=weld, welder=welder_no)
        wpq_models.Wpq.objects.create(
            welder=welder_ok,
            code="WPQ-OK",
            standard="ASME_IX",
            status="approved",
        )

        response = self.client.get(reverse("project_detail", args=[project.id]))
        self.assertEqual(response.status_code, 200)
        rows = response.context["welder_qualification"]
        by_name = {row["welder"].name: row["has_wpq"] for row in rows}
        self.assertTrue(by_name["Welder OK"])
        self.assertFalse(by_name["Welder NO"])

    def test_project_copy_creates_new_project_with_equipment(self):
        project = models.Project.objects.create(
            name="Project Copy Source",
            code="00000020",
            purchase_order="PO-20",
            units="metric",
            status="active",
            standard_set=["ASME_IX"],
        )
        models.ProjectEquipment.objects.create(
            project=project,
            name="Vessel A",
            fabrication_code="EQ-001",
            status="active",
        )

        response = self.client.post(reverse("project_copy", args=[project.id]))
        self.assertEqual(response.status_code, 302)

        copied = models.Project.objects.get(code="00000020-COPY")
        self.assertEqual(copied.name, "Project Copy Source (Copy)")
        self.assertEqual(
            models.ProjectEquipment.objects.filter(project=copied).count(),
            1,
        )

    def test_project_delete_removes_project(self):
        project = models.Project.objects.create(
            name="Project Delete",
            code="00000030",
            units="metric",
            status="active",
            standard_set=["ASME_IX"],
        )

        response = self.client.post(reverse("project_delete", args=[project.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(models.Project.objects.filter(id=project.id).exists())
