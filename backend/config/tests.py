from django.test import TestCase

from apps.documents import models as document_models
from apps.projects import models as project_models
from apps.welds import models as weld_models
from apps.wpq import models as wpq_models
from apps.wps import models as wps_models


class HomeDashboardTests(TestCase):
    def test_home_lists_projects_with_summary_counts(self):
        project_1 = project_models.Project.objects.create(
            name="Proyecto Uno",
            code="P1",
            units="metric",
            status="active",
            standard_set=["ASME_IX"],
        )
        project_2 = project_models.Project.objects.create(
            name="Proyecto Dos",
            code="P2",
            units="metric",
            status="active",
            standard_set=["ASME_IX"],
        )

        document_models.Document.objects.create(
            project=project_1,
            type="Welding Book",
            title="Welding Book A",
            status="active",
        )
        document_models.Document.objects.create(
            project=project_1,
            type="Procedure",
            title="Procedure notes",
            status="active",
        )
        document_models.Document.objects.create(
            project=project_1,
            type="General",
            title="Welding Book - Extra",
            status="active",
        )

        wps_models.Wps.objects.create(
            project=project_1, code="WPS-001", standard="ASME_IX", status="draft"
        )
        wps_models.Wps.objects.create(
            project=project_1, code="WPS-002", standard="ASME_IX", status="draft"
        )
        wps_models.Wps.objects.create(
            project=project_2, code="WPS-101", standard="ASME_IX", status="draft"
        )

        wps_models.Pqr.objects.create(
            project=project_1, code="PQR-001", standard="ASME_IX", status="draft"
        )

        weld_1 = weld_models.Weld.objects.create(project=project_1, number="W1")
        weld_2 = weld_models.Weld.objects.create(project=project_1, number="W2")
        weld_3 = weld_models.Weld.objects.create(project=project_2, number="W1")

        welder_1 = wpq_models.Welder.objects.create(name="Welder 1")
        welder_2 = wpq_models.Welder.objects.create(name="Welder 2")
        welder_3 = wpq_models.Welder.objects.create(name="Welder 3")

        weld_models.WeldWelderAssignment.objects.create(weld=weld_1, welder=welder_1)
        weld_models.WeldWelderAssignment.objects.create(weld=weld_2, welder=welder_1)
        weld_models.WeldWelderAssignment.objects.create(weld=weld_2, welder=welder_2)
        weld_models.WeldWelderAssignment.objects.create(weld=weld_3, welder=welder_3)

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        projects = {item.code: item for item in response.context["projects"]}
        self.assertEqual(projects["P1"].welding_book_count, 2)
        self.assertEqual(projects["P1"].wps_count, 2)
        self.assertEqual(projects["P1"].pqr_count, 1)
        self.assertEqual(projects["P1"].welder_count, 2)

        self.assertEqual(projects["P2"].welding_book_count, 0)
        self.assertEqual(projects["P2"].wps_count, 1)
        self.assertEqual(projects["P2"].pqr_count, 0)
        self.assertEqual(projects["P2"].welder_count, 1)
