from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.users import models as user_models
from apps.projects import models as project_models
from . import models


class WeldCloseTests(TestCase):
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

    def test_close_weld_changes_status(self):
        weld = models.Weld.objects.create(
            project=self.project, number="W1", status="in_progress"
        )
        resp = self.client.post(f"/api/welds/{weld.id}/close/", format="json")
        self.assertEqual(resp.status_code, 200)
        weld.refresh_from_db()
        self.assertEqual(weld.status, "completed")


class WeldMapUiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.app_user = user_models.User.objects.create(
            name="ui-admin", email="ui-admin@example.local", status="active"
        )
        role, _ = user_models.Role.objects.get_or_create(name="Admin", defaults={"scope": "global"})
        user_models.UserRole.objects.get_or_create(user=self.app_user, role=role)
        self.project = project_models.Project.objects.create(
            name="P-UI", code="P-UI", units="metric", status="active", standard_set=["ASME_IX"]
        )
        project_models.ProjectUser.objects.create(
            project=self.project, user=self.app_user, role=role
        )
        self.auth_user = self._auth_user()
        self.client.force_login(self.auth_user)
        self.drawing = models.Drawing.objects.create(
            project=self.project,
            code="DRW-001",
            revision="A",
            file_path="",
            status="active",
        )
        self.weld_map = models.WeldMap.objects.create(
            project=self.project,
            drawing=self.drawing,
            status="active",
        )
        self.equipment = project_models.ProjectEquipment.objects.create(
            project=self.project,
            name="V-100",
            fabrication_code="EQ-100",
            status="active",
        )

    def _auth_user(self):
        from django.contrib.auth import get_user_model

        AuthUser = get_user_model()
        auth_user, _ = AuthUser.objects.get_or_create(
            username="ui-admin", defaults={"email": self.app_user.email}
        )
        return auth_user

    def test_save_marks_creates_auto_numbered_weld(self):
        url = reverse("weld_map_detail", kwargs={"pk": self.weld_map.id})
        resp = self.client.post(
            url,
            {
                "action": "save_marks",
                "number_prefix": "S",
                "marks_json": '[{"geometry":{"type":"circle","cx":100,"cy":140,"r":12}}]',
                "attributes_json": "[]",
                "geometry_json": "",
                "weld_number": "",
            },
            format="multipart",
        )
        self.assertEqual(resp.status_code, 302)
        weld = models.Weld.objects.get(project=self.project, number="S1")
        self.assertEqual(weld.drawing_id, self.drawing.id)
        self.assertTrue(
            models.WeldMark.objects.filter(weld_map=self.weld_map, weld=weld).exists()
        )

    def test_save_welding_list_updates_attributes(self):
        weld = models.Weld.objects.create(
            project=self.project,
            drawing=self.drawing,
            number="S10",
            status="planned",
        )
        models.WeldMark.objects.create(
            weld_map=self.weld_map,
            weld=weld,
            geometry={"type": "circle", "cx": 10, "cy": 15, "r": 5},
        )
        models.WeldAttribute.objects.create(weld=weld, name="weld_type", value="OLD")
        url = reverse("weld_map_detail", kwargs={"pk": self.weld_map.id})
        resp = self.client.post(
            url,
            {
                "action": "save_weld_list",
                f"joint_description_{weld.id}": "PIPE-TO-PIPE",
                f"weld_type_{weld.id}": "BW",
                f"p_no_grade_{weld.id}": "",
                f"wps_no_{weld.id}": "WPS-001",
                f"pqr_no_{weld.id}": "PQR-001",
                f"position_{weld.id}": "6G",
                f"processes_{weld.id}": "GTAW,SMAW",
                f"base_material_{weld.id}": "A106 Gr.B",
            },
            format="multipart",
        )
        self.assertEqual(resp.status_code, 302)
        values = {
            row.name: row.value
            for row in models.WeldAttribute.objects.filter(weld=weld)
        }
        self.assertEqual(values["joint_description"], "PIPE-TO-PIPE")
        self.assertEqual(values["weld_type"], "BW")
        self.assertEqual(values["wps_no"], "WPS-001")
        self.assertNotIn("p_no_grade", values)

    def test_create_weld_map_rejects_drawing_from_other_project(self):
        other_project = project_models.Project.objects.create(
            name="P-OTHER",
            code="P-OTHER",
            units="metric",
            status="active",
            standard_set=["ASME_IX"],
        )
        foreign_drawing = models.Drawing.objects.create(
            project=other_project,
            code="DRW-999",
            revision="A",
            file_path="",
            status="active",
        )
        url = reverse("weld_map_create")
        resp = self.client.post(
            url,
            {
                "project": str(self.project.id),
                "drawing": str(foreign_drawing.id),
                "status": "active",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Drawing does not belong to the project.")
        self.assertFalse(
            models.WeldMap.objects.filter(
                project=self.project,
                drawing=foreign_drawing,
            ).exists()
        )

    def test_weld_map_list_upload_pdf_creates_or_opens_map(self):
        pdf = SimpleUploadedFile(
            "isometric.pdf",
            b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
            content_type="application/pdf",
        )
        url = reverse("weld_map_list")
        resp = self.client.post(
            url,
            {
                "action": "create_from_pdf",
                "project": str(self.project.id),
                "equipment": str(self.equipment.id),
                "drawing_code": "ISO-100",
                "revision": "A",
                "upload": pdf,
            },
        )
        self.assertEqual(resp.status_code, 302)
        drawing = models.Drawing.objects.get(
            project=self.project,
            code="ISO-100",
            revision="A",
        )
        self.assertEqual(drawing.equipment_id, self.equipment.id)
        self.assertTrue(drawing.file_path.replace("\\", "/").startswith("drawings/"))
        weld_map = models.WeldMap.objects.get(project=self.project, drawing=drawing)
        self.assertIn(str(weld_map.id), resp["Location"])

    def test_delete_saved_mark_removes_mark(self):
        weld = models.Weld.objects.create(
            project=self.project,
            drawing=self.drawing,
            number="S20",
            status="planned",
        )
        mark = models.WeldMark.objects.create(
            weld_map=self.weld_map,
            weld=weld,
            geometry={"type": "circle", "cx": 20, "cy": 20, "r": 8},
        )
        url = reverse("weld_map_detail", kwargs={"pk": self.weld_map.id})
        resp = self.client.post(
            url,
            {
                "action": "delete_saved_mark",
                "mark_id": str(mark.id),
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(models.WeldMark.objects.filter(id=mark.id).exists())

    def test_update_saved_mark_geometry(self):
        weld = models.Weld.objects.create(
            project=self.project,
            drawing=self.drawing,
            number="S30",
            status="planned",
        )
        mark = models.WeldMark.objects.create(
            weld_map=self.weld_map,
            weld=weld,
            geometry={"type": "circle", "cx": 25, "cy": 25, "r": 10},
        )
        url = reverse("weld_map_detail", kwargs={"pk": self.weld_map.id})
        resp = self.client.post(
            url,
            {
                "action": "update_saved_mark",
                "mark_id": str(mark.id),
                "geometry_json": '{"type":"circle","cx":42,"cy":77,"r":15}',
            },
        )
        self.assertEqual(resp.status_code, 302)
        mark.refresh_from_db()
        self.assertEqual(mark.geometry["cx"], 42)
        self.assertEqual(mark.geometry["cy"], 77)
        self.assertEqual(mark.geometry["r"], 15)

    def test_update_saved_mark_ref_changes_weld_number(self):
        weld = models.Weld.objects.create(
            project=self.project,
            drawing=self.drawing,
            number="S40",
            status="planned",
        )
        mark = models.WeldMark.objects.create(
            weld_map=self.weld_map,
            weld=weld,
            geometry={"type": "circle", "cx": 30, "cy": 30, "r": 10},
        )
        url = reverse("weld_map_detail", kwargs={"pk": self.weld_map.id})
        resp = self.client.post(
            url,
            {
                "action": "update_saved_mark_ref",
                "mark_id": str(mark.id),
                "weld_number": "S99",
            },
        )
        self.assertEqual(resp.status_code, 302)
        mark.refresh_from_db()
        self.assertEqual(mark.weld.number, "S99")

    def test_update_saved_mark_ref_rejects_duplicate_in_same_map(self):
        weld_a = models.Weld.objects.create(
            project=self.project,
            drawing=self.drawing,
            number="S50",
            status="planned",
        )
        weld_b = models.Weld.objects.create(
            project=self.project,
            drawing=self.drawing,
            number="S51",
            status="planned",
        )
        mark_a = models.WeldMark.objects.create(
            weld_map=self.weld_map,
            weld=weld_a,
            geometry={"type": "circle", "cx": 10, "cy": 10, "r": 6},
        )
        mark_b = models.WeldMark.objects.create(
            weld_map=self.weld_map,
            weld=weld_b,
            geometry={"type": "circle", "cx": 40, "cy": 40, "r": 9},
        )
        url = reverse("weld_map_detail", kwargs={"pk": self.weld_map.id})
        resp = self.client.post(
            url,
            {
                "action": "update_saved_mark_ref",
                "mark_id": str(mark_b.id),
                "weld_number": "S50",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "ya existe en este welding map")
        mark_b.refresh_from_db()
        self.assertEqual(mark_b.weld.number, "S51")

    def test_save_marks_rejects_duplicate_ref_in_same_map(self):
        existing_weld = models.Weld.objects.create(
            project=self.project,
            drawing=self.drawing,
            number="S60",
            status="planned",
        )
        models.WeldMark.objects.create(
            weld_map=self.weld_map,
            weld=existing_weld,
            geometry={"type": "circle", "cx": 5, "cy": 5, "r": 3},
        )
        url = reverse("weld_map_detail", kwargs={"pk": self.weld_map.id})
        resp = self.client.post(
            url,
            {
                "action": "save_marks",
                "number_prefix": "S",
                "marks_json": '[{"number":"S60","geometry":{"type":"circle","cx":100,"cy":120,"r":12}}]',
                "attributes_json": "[]",
                "geometry_json": "",
                "weld_number": "",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "No se permiten referencias duplicadas en el map")
        self.assertEqual(
            models.WeldMark.objects.filter(weld_map=self.weld_map, weld__number="S60").count(),
            1,
        )
