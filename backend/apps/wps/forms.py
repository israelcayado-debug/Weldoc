from django import forms

from . import models


class WpsQuickCreateForm(forms.Form):
    PROCESS_CHOICES = [("", "---")] + list(models.WpsProcess.PROCESS_CHOICES)
    SPECIAL_CHOICES = [("", "---")] + list(models.WpsProcess.SPECIAL_CHOICES)

    project = forms.ModelChoiceField(
        queryset=models.Wps._meta.get_field("project").related_model.objects.all(),
        required=False,
    )
    equipment = forms.ModelChoiceField(
        queryset=models.Wps._meta.get_field("equipment").related_model.objects.none(),
        required=False,
    )
    code = forms.CharField(max_length=100)
    standard = forms.CharField(max_length=30, initial="ASME_IX")
    impact_test = forms.BooleanField(required=False)
    status = forms.ChoiceField(
        choices=(
            ("draft", "Draft"),
            ("in_review", "In review"),
            ("approved", "Approved"),
            ("archived", "Archived"),
        ),
        initial="draft",
    )

    process_1 = forms.ChoiceField(choices=PROCESS_CHOICES, required=False)
    special_process_1 = forms.ChoiceField(choices=SPECIAL_CHOICES, required=False)
    process_2 = forms.ChoiceField(choices=PROCESS_CHOICES, required=False)
    special_process_2 = forms.ChoiceField(choices=SPECIAL_CHOICES, required=False)
    process_3 = forms.ChoiceField(choices=PROCESS_CHOICES, required=False)
    special_process_3 = forms.ChoiceField(choices=SPECIAL_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        equipment_model = models.Wps._meta.get_field("equipment").related_model
        project_id = None
        if "project" in self.data:
            project_id = self.data.get("project")
        elif self.initial.get("project"):
            project_id = self.initial.get("project")
        if project_id:
            self.fields["equipment"].queryset = equipment_model.objects.filter(
                project_id=project_id
            ).order_by("name")
        else:
            self.fields["equipment"].queryset = equipment_model.objects.order_by("name")

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status not in ("draft", "in_review", "approved", "archived"):
            raise forms.ValidationError("Invalid status.")
        return status

    def clean(self):
        cleaned = super().clean()
        project = cleaned.get("project")
        equipment = cleaned.get("equipment")
        if project and equipment and equipment.project_id != project.id:
            self.add_error("equipment", "Equipment does not belong to the selected project.")
        selected = []
        for index in range(1, 4):
            process = cleaned.get(f"process_{index}")
            special = cleaned.get(f"special_process_{index}")
            if not process:
                if special:
                    self.add_error(f"special_process_{index}", "Select a process first.")
                continue
            if process != "SMAW" and special:
                self.add_error(
                    f"special_process_{index}",
                    "Special process applies only to SMAW.",
                )
            selected.append(process)
        if not selected:
            self.add_error("process_1", "Add at least one process.")
        if len(selected) != len(set(selected)):
            self.add_error("process_1", "Processes must be unique.")
        return cleaned

    def save(self):
        item = models.Wps.objects.create(
            project=self.cleaned_data["project"],
            equipment=self.cleaned_data.get("equipment"),
            code=self.cleaned_data["code"],
            standard=self.cleaned_data["standard"],
            impact_test=self.cleaned_data["impact_test"],
            status=self.cleaned_data["status"],
        )
        order = 1
        for index in range(1, 4):
            process = self.cleaned_data.get(f"process_{index}")
            if not process:
                continue
            special = self.cleaned_data.get(f"special_process_{index}") or None
            if process != "SMAW":
                special = None
            models.WpsProcess.objects.create(
                wps=item,
                process_code=process,
                special_process=special,
                order=order,
            )
            order += 1
        return item


class PqrQuickCreateForm(forms.Form):
    code = forms.CharField(max_length=100)
    standard = forms.CharField(max_length=30, initial="ASME_IX")
    status = forms.ChoiceField(
        choices=(
            ("draft", "Draft"),
            ("in_review", "In review"),
            ("approved", "Approved"),
            ("archived", "Archived"),
        ),
        initial="draft",
    )
    processes = forms.CharField(max_length=100, label="PROCESO")
    thickness_range = forms.CharField(max_length=100, label="T (mm) 403.6")
    material_1 = forms.CharField(max_length=200, label="MATERIAL")
    p_group_1 = forms.CharField(max_length=100, label="N° MATERIAL 1")
    material_2 = forms.CharField(max_length=200, label="MATERIAL 2")
    p_group_2 = forms.CharField(max_length=100, label="N° MATERIAL 2")
    p_group = forms.CharField(max_length=120, label="N° P & GROUP")
    filler_fno_gtaw = forms.CharField(max_length=120, label="N° F GTAW")
    a_no_gtaw = forms.CharField(max_length=120, label="N° A GTAW")
    filler_fno_smaw = forms.CharField(max_length=120, label="N° F SMAW")
    a_no_smaw = forms.CharField(max_length=120, label="N° A SMAW")
    gtaw_filler_form = forms.CharField(max_length=120, label="GTAW Filler and Form")
    diameter = forms.CharField(max_length=100, label="DIÁMETRO")
    thickness_test_coupon = forms.CharField(max_length=100, label="ESPESOR CUPÓN")
    t_max_gtaw = forms.CharField(max_length=100, label="t max GTAW")
    t_max_smaw = forms.CharField(max_length=100, label="t max SMAW")
    preheat = forms.CharField(max_length=100, label="PREHEAT")
    pwht = forms.CharField(max_length=120, label="PWHT 407.2")
    gas_protection = forms.CharField(max_length=120, label="GAS PROTECCION")
    aws_sfa_gtaw = forms.CharField(max_length=120, label="AWS SFA GTAW 404.12")
    aws_sfa_smaw = forms.CharField(max_length=120, label="AWS SFA SMAW 404.12")
    interpass_temp = forms.CharField(max_length=120, label="Tª ENTRE PASADAS 406.3")
    heat_input_gtaw = forms.CharField(max_length=120, label="A. TERMIC. GTAW KJ/cm 409.1")
    heat_input_smaw = forms.CharField(max_length=120, label="A. TERMIC. SMAW KJ/cm 409.1")
    base_metal_a_no = forms.CharField(max_length=120, label="N° A M. BASE 403.5")
    position = forms.CharField(max_length=120, label="POSICION 405.2")
    gas_backing = forms.CharField(max_length=120, label="GAS RESPALDO")
    end_requirements = forms.CharField(max_length=300, label="END")
    itm_signature = forms.CharField(max_length=120, label="FIRMA ITM")
    notes = forms.CharField(max_length=300, label="NOTAS", required=False)

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status not in ("draft", "in_review", "approved", "archived"):
            raise forms.ValidationError("Invalid status.")
        return status

    def clean_code(self):
        code = (self.cleaned_data.get("code") or "").strip()
        if models.Pqr.objects.filter(code=code).exists():
            raise forms.ValidationError("PQR code already exists.")
        return code

    def save(self):
        item = models.Pqr.objects.create(
            code=self.cleaned_data["code"],
            standard=self.cleaned_data["standard"],
            status=self.cleaned_data["status"],
            project=None,
        )
        result_map = {
            "processes": self.cleaned_data.get("processes"),
            "thickness_range": self.cleaned_data.get("thickness_range"),
            "material_1": self.cleaned_data.get("material_1"),
            "p_group_1": self.cleaned_data.get("p_group_1"),
            "material_2": self.cleaned_data.get("material_2"),
            "p_group_2": self.cleaned_data.get("p_group_2"),
            "material_pno": self.cleaned_data.get("p_group"),
            "filler_fno": self.cleaned_data.get("filler_fno_gtaw"),
            "filler_fno_gtaw": self.cleaned_data.get("filler_fno_gtaw"),
            "a_no_gtaw": self.cleaned_data.get("a_no_gtaw"),
            "filler_fno_smaw": self.cleaned_data.get("filler_fno_smaw"),
            "a_no_smaw": self.cleaned_data.get("a_no_smaw"),
            "gtaw_filler_form": self.cleaned_data.get("gtaw_filler_form"),
            "diameter": self.cleaned_data.get("diameter"),
            "thickness_test_coupon": self.cleaned_data.get("thickness_test_coupon"),
            "t_max_gtaw": self.cleaned_data.get("t_max_gtaw"),
            "t_max_smaw": self.cleaned_data.get("t_max_smaw"),
            "preheat": self.cleaned_data.get("preheat"),
            "pwht": self.cleaned_data.get("pwht"),
            "gas_protection": self.cleaned_data.get("gas_protection"),
            "aws_sfa_gtaw": self.cleaned_data.get("aws_sfa_gtaw"),
            "aws_sfa_smaw": self.cleaned_data.get("aws_sfa_smaw"),
            "interpass_temp": self.cleaned_data.get("interpass_temp"),
            "heat_input_gtaw": self.cleaned_data.get("heat_input_gtaw"),
            "heat_input_smaw": self.cleaned_data.get("heat_input_smaw"),
            "base_metal_a_no": self.cleaned_data.get("base_metal_a_no"),
            "position": self.cleaned_data.get("position"),
            "gas_backing": self.cleaned_data.get("gas_backing"),
            "end": self.cleaned_data.get("end_requirements"),
            "itm_signature": self.cleaned_data.get("itm_signature"),
            "notes": self.cleaned_data.get("notes"),
        }
        for test_type, value in result_map.items():
            text = "" if value is None else str(value).strip()
            if not text:
                continue
            models.PqrResult.objects.create(
                pqr=item,
                test_type=test_type,
                result=text,
            )
        return item


class PqrScanUploadForm(forms.Form):
    scan_pdf = forms.FileField(label="Escaneado oficial del PQR (PDF)")

    def clean_scan_pdf(self):
        scan_pdf = self.cleaned_data["scan_pdf"]
        filename = (scan_pdf.name or "").lower()
        if not filename.endswith(".pdf"):
            raise forms.ValidationError("Only PDF files are allowed.")
        return scan_pdf


class WpsForm(forms.ModelForm):
    class Meta:
        model = models.Wps
        fields = ["project", "equipment", "code", "standard", "impact_test", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].disabled = True
        if not getattr(self.instance, "pk", None):
            self.fields["status"].initial = models.Wps.STATUS_DRAFT
        equipment_model = models.Wps._meta.get_field("equipment").related_model
        project_id = None
        if self.instance and self.instance.project_id:
            project_id = self.instance.project_id
        if "project" in self.data:
            project_id = self.data.get("project")
        elif self.initial.get("project"):
            project_id = self.initial.get("project")
        if project_id:
            self.fields["equipment"].queryset = equipment_model.objects.filter(
                project_id=project_id
            ).order_by("name")
        else:
            self.fields["equipment"].queryset = equipment_model.objects.order_by("name")

    def clean_status(self):
        status = self.cleaned_data.get("status") or models.Wps.STATUS_DRAFT
        allowed = {
            models.Wps.STATUS_DRAFT,
            models.Wps.STATUS_PENDING_APPROVAL,
            models.Wps.STATUS_REVIEWED,
            models.Wps.STATUS_APPROVED,
            models.Wps.STATUS_ARCHIVED,
        }
        if status not in allowed:
            raise forms.ValidationError("Invalid status.")
        return status

    def clean(self):
        cleaned = super().clean()
        project = cleaned.get("project")
        equipment = cleaned.get("equipment")
        if project and equipment and equipment.project_id != project.id:
            self.add_error("equipment", "Equipment does not belong to the selected project.")
        return cleaned


class WpsProcessForm(forms.ModelForm):
    class Meta:
        model = models.WpsProcess
        fields = ["wps", "process_code", "special_process", "order"]
        widgets = {
            "wps": forms.HiddenInput(),
        }

    def clean(self):
        cleaned = super().clean()
        wps = cleaned.get("wps")
        process_code = cleaned.get("process_code")
        special_process = cleaned.get("special_process")
        if wps and process_code:
            existing = models.WpsProcess.objects.filter(
                wps=wps, process_code=process_code
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                self.add_error("process_code", "Process already added to this WPS.")
            if models.WpsProcess.objects.filter(wps=wps).exclude(pk=self.instance.pk).count() >= 3:
                self.add_error("process_code", "A WPS can have up to 3 processes.")
        if process_code != "SMAW" and special_process:
            self.add_error("special_process", "Special process applies only to SMAW.")
        return cleaned


class WpsVariableBulkForm(forms.Form):
    def __init__(self, definitions, required_ids=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_ids = set(required_ids or [])
        for definition in definitions:
            field_name = f"var_{definition.id}"
            required = definition.id in required_ids
            if definition.data_type == "number":
                field = forms.DecimalField(required=required)
            elif definition.data_type == "boolean":
                field = forms.BooleanField(required=False)
            elif definition.data_type == "enum":
                choices = [(opt, opt) for opt in (definition.options_json or [])]
                field = forms.ChoiceField(required=required, choices=choices)
            else:
                field = forms.CharField(required=required)
            field.label = definition.label
            if definition.unit:
                field.help_text = f"Unit: {definition.unit}"
            self.fields[field_name] = field
