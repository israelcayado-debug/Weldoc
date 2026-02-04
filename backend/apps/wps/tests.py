import shutil
import tempfile

from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APIClient

from apps.users import models as user_models
from apps.projects import models as project_models
from . import models


class WpsApproveTests(TestCase):
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
        self.user = self.client.force_authenticate(user=self._auth_user())

    def _auth_user(self):
        from django.contrib.auth import get_user_model

        AuthUser = get_user_model()
        auth_user, _ = AuthUser.objects.get_or_create(
            username="admin", defaults={"email": self.app_user.email}
        )
        return auth_user

    def test_wps_approve_requires_pqr(self):
        wps = models.Wps.objects.create(
            project=self.project, code="WPS-1", standard="ASME_IX", status="draft"
        )
        resp = self.client.post(f"/api/wps/{wps.id}/approve/", {"pqr_ids": []}, format="json")
        self.assertEqual(resp.status_code, 400)


class WpsUiToolTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        AuthUser = get_user_model()
        self.user = AuthUser.objects.create_user(username="ui-user", password="12345")
        self.client.login(username="ui-user", password="12345")
        self.project = project_models.Project.objects.create(
            name="P1", code="P1", units="metric", status="active", standard_set=["ASME_IX"]
        )

    def test_create_tool_creates_wps_and_processes(self):
        resp = self.client.post(
            reverse("wps_create_tool"),
            {
                "project": str(self.project.id),
                "code": "WPS-TOOL-001",
                "standard": "ASME_IX",
                "impact_test": "on",
                "status": "draft",
                "process_1": "SMAW",
                "special_process_1": "HFO",
                "process_2": "GTAW",
                "special_process_2": "",
                "process_3": "",
                "special_process_3": "",
            },
        )
        self.assertEqual(resp.status_code, 302)
        item = models.Wps.objects.get(code="WPS-TOOL-001")
        self.assertEqual(item.project_id, self.project.id)
        self.assertTrue(item.impact_test)
        processes = list(models.WpsProcess.objects.filter(wps=item).order_by("order"))
        self.assertEqual(len(processes), 2)
        self.assertEqual(processes[0].process_code, "SMAW")
        self.assertEqual(processes[0].special_process, "HFO")
        self.assertEqual(processes[1].process_code, "GTAW")
        self.assertIsNone(processes[1].special_process)
        self.assertIn(f"/ui/wps/{item.id}/qw482/", resp.url)

    def test_create_tool_requires_at_least_one_process(self):
        resp = self.client.post(
            reverse("wps_create_tool"),
            {
                "project": str(self.project.id),
                "code": "WPS-TOOL-002",
                "standard": "ASME_IX",
                "status": "draft",
                "process_1": "",
                "special_process_1": "",
                "process_2": "",
                "special_process_2": "",
                "process_3": "",
                "special_process_3": "",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Add at least one process.")
        self.assertFalse(models.Wps.objects.filter(code="WPS-TOOL-002").exists())


class WpsListUiTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        AuthUser = get_user_model()
        self.user = AuthUser.objects.create_user(username="wps-list-ui", password="12345")
        self.client.login(username="wps-list-ui", password="12345")
        self.project = project_models.Project.objects.create(
            name="P1",
            code="P1",
            units="metric",
            status="active",
            standard_set=["ASME_IX"],
        )

    def test_list_shows_project_p_numbers_and_applicable_pqr(self):
        wps = models.Wps.objects.create(
            project=self.project,
            code="WPS-LIST-001",
            standard="ASME_IX",
            status="draft",
        )
        pqr = models.Pqr.objects.create(
            project=self.project,
            code="PQR-LIST-001",
            standard="ASME_IX",
            status="approved",
        )
        models.WpsPqrLink.objects.create(wps=wps, pqr=pqr)
        process = models.WpsProcess.objects.create(wps=wps, process_code="SMAW", order=1)
        definition = models.WpsVariableDefinition.objects.create(
            process_code="SMAW",
            special_process=None,
            category="essential",
            code="QW-403.11",
            name="p_no_qualified",
            label="P-No. qualified",
            data_type="text",
        )
        models.WpsVariableValue.objects.create(
            wps_process=process,
            definition=definition,
            value="P-No.1",
        )

        response = self.client.get("/ui/wps/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "WPS-LIST-001")
        self.assertContains(response, "P1")
        self.assertContains(response, "P-No.1")
        self.assertContains(response, "PQR-LIST-001")

    def test_copy_creates_new_wps_with_processes_and_values(self):
        wps = models.Wps.objects.create(
            project=self.project,
            code="WPS-SRC-001",
            standard="ASME_IX",
            status="approved",
            impact_test=True,
        )
        process = models.WpsProcess.objects.create(
            wps=wps, process_code="SMAW", special_process="HFO", order=1
        )
        definition = models.WpsVariableDefinition.objects.create(
            process_code="SMAW",
            special_process="HFO",
            category="essential",
            code="QW-403.11-COPY",
            name="p_no_qualified_copy",
            label="P-No. qualified copy",
            data_type="text",
        )
        models.WpsVariableValue.objects.create(
            wps_process=process,
            definition=definition,
            value="P-No.8",
        )

        response = self.client.post(f"/ui/wps/{wps.id}/copy/")
        self.assertEqual(response.status_code, 302)

        copied = models.Wps.objects.get(code="WPS-SRC-001-COPY")
        self.assertEqual(copied.project_id, wps.project_id)
        self.assertEqual(copied.standard, wps.standard)
        self.assertTrue(copied.impact_test)
        self.assertEqual(copied.status, "draft")

        copied_processes = list(models.WpsProcess.objects.filter(wps=copied))
        self.assertEqual(len(copied_processes), 1)
        self.assertEqual(copied_processes[0].process_code, "SMAW")
        self.assertEqual(copied_processes[0].special_process, "HFO")
        copied_values = list(models.WpsVariableValue.objects.filter(wps_process=copied_processes[0]))
        self.assertEqual(len(copied_values), 1)
        self.assertEqual(copied_values[0].value, "P-No.8")


class PqrUiToolTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        self.media_root = tempfile.mkdtemp()
        self._media_override = override_settings(MEDIA_ROOT=self.media_root)
        self._media_override.enable()

        AuthUser = get_user_model()
        self.user = AuthUser.objects.create_user(username="ui-user-pqr", password="12345")
        self.client.login(username="ui-user-pqr", password="12345")
        self.project = project_models.Project.objects.create(
            name="P1", code="P1", units="metric", status="active", standard_set=["ASME_IX"]
        )

    def tearDown(self):
        self._media_override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)
        super().tearDown()

    def test_create_tool_creates_pqr_and_results(self):
        resp = self.client.post(
            reverse("pqr_create_tool"),
            {
                "code": "PQR-TOOL-001",
                "standard": "ASME_IX",
                "status": "draft",
                "processes": "SMAW,GTAW",
                "thickness_range": "3 a 12",
                "material_1": "SA335 P5",
                "p_group_1": "P5B",
                "material_2": "SA335 P5",
                "p_group_2": "P5B",
                "p_group": "P5B con P5B",
                "filler_fno_gtaw": "6",
                "a_no_gtaw": "5",
                "filler_fno_smaw": "4",
                "a_no_smaw": "5",
                "gtaw_filler_form": "CON/SOLIDO",
                "diameter": "273",
                "thickness_test_coupon": "25",
                "t_max_gtaw": "14",
                "t_max_smaw": "6",
                "preheat": ">145",
                "pwht": "750, 2 h",
                "gas_protection": "ARGON 99,9%",
                "aws_sfa_gtaw": "ER-80S-B8",
                "aws_sfa_smaw": "E-8015-B8",
                "interpass_temp": "406 C Max",
                "heat_input_gtaw": "32,64 Max",
                "heat_input_smaw": "33,15 Max",
                "base_metal_a_no": "A1 con A1",
                "position": "All",
                "gas_backing": "CON/SIN",
                "end_requirements": "TRACCION Y PLEGADO, MACROGRAFIA, DUREZAS",
                "itm_signature": "ITM-001",
                "notes": "Certificado OK",
            },
        )
        self.assertEqual(resp.status_code, 302)
        item = models.Pqr.objects.get(code="PQR-TOOL-001")
        self.assertIsNone(item.project_id)
        results = list(models.PqrResult.objects.filter(pqr=item))
        self.assertEqual(len(results), 31)
        self.assertIn(f"/ui/pqr/{item.id}/", resp.url)

    def test_create_tool_requires_required_fields(self):
        resp = self.client.post(
            reverse("pqr_create_tool"),
            {
                "code": "PQR-TOOL-002",
                "standard": "ASME_IX",
                "status": "draft",
                "processes": "",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Este campo es requerido.")
        self.assertFalse(models.Pqr.objects.filter(code="PQR-TOOL-002").exists())

    def test_submit_review_changes_status(self):
        item = models.Pqr.objects.create(
            project=self.project, code="PQR-REVIEW-001", standard="ASME_IX", status="draft"
        )
        resp = self.client.post(reverse("pqr_submit_review", kwargs={"pk": item.id}))
        self.assertEqual(resp.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.status, "in_review")

    def test_approve_changes_status_when_has_results(self):
        item = models.Pqr.objects.create(
            project=self.project, code="PQR-APPROVE-001", standard="ASME_IX", status="in_review"
        )
        models.PqrResult.objects.create(
            pqr=item,
            test_type="processes",
            result="SMAW",
        )
        resp = self.client.post(reverse("pqr_approve", kwargs={"pk": item.id}))
        self.assertEqual(resp.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.status, "approved")

    def test_approve_keeps_status_without_results(self):
        item = models.Pqr.objects.create(
            project=self.project, code="PQR-APPROVE-002", standard="ASME_IX", status="in_review"
        )
        resp = self.client.post(reverse("pqr_approve", kwargs={"pk": item.id}))
        self.assertEqual(resp.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.status, "in_review")

    def test_upload_scan_pdf_sets_file(self):
        item = models.Pqr.objects.create(
            project=self.project, code="PQR-SCAN-001", standard="ASME_IX", status="draft"
        )
        payload = {
            "scan_pdf": SimpleUploadedFile(
                "pqr-scan.pdf",
                b"%PDF-1.4 test file",
                content_type="application/pdf",
            )
        }
        resp = self.client.post(
            reverse("pqr_upload_scan", kwargs={"pk": item.id}),
            payload,
        )
        self.assertEqual(resp.status_code, 302)
        item.refresh_from_db()
        self.assertTrue(bool(item.scanned_pdf))

    def test_upload_scan_rejects_non_pdf(self):
        item = models.Pqr.objects.create(
            project=self.project, code="PQR-SCAN-002", standard="ASME_IX", status="draft"
        )
        payload = {
            "scan_pdf": SimpleUploadedFile(
                "pqr-scan.txt",
                b"not-a-pdf",
                content_type="text/plain",
            )
        }
        resp = self.client.post(
            reverse("pqr_upload_scan", kwargs={"pk": item.id}),
            payload,
        )
        self.assertEqual(resp.status_code, 400)
        item.refresh_from_db()
        self.assertFalse(bool(item.scanned_pdf))
