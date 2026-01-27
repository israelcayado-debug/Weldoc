from django import forms
import json

from . import models
from apps.projects import models as project_models


class WeldForm(forms.ModelForm):
    class Meta:
        model = models.Weld
        fields = ["project", "drawing", "number", "status"]

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status not in ("planned", "in_progress", "completed", "repair"):
            raise forms.ValidationError("Invalid status.")
        return status


class DrawingForm(forms.ModelForm):
    upload = forms.FileField(required=False)

    class Meta:
        model = models.Drawing
        fields = ["project", "equipment", "code", "revision", "file_path", "status"]
        widgets = {
            "file_path": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file_path"].required = False
        self.fields["equipment"].required = True
        project_id = None
        if self.instance and self.instance.project_id:
            project_id = self.instance.project_id
        if "project" in self.data:
            project_id = self.data.get("project")
        elif self.initial.get("project"):
            project_id = self.initial.get("project")
        if project_id:
            self.fields["equipment"].queryset = project_models.ProjectEquipment.objects.filter(
                project_id=project_id
            ).order_by("name")

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status not in ("active", "archived"):
            raise forms.ValidationError("Invalid status.")
        return status

    def clean(self):
        cleaned = super().clean()
        project = cleaned.get("project")
        equipment = cleaned.get("equipment")
        if project and equipment and equipment.project_id != project.id:
            self.add_error("equipment", "Equipment does not belong to the project.")
        return cleaned


class WeldMapForm(forms.ModelForm):
    class Meta:
        model = models.WeldMap
        fields = ["project", "drawing", "status"]

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status not in ("active", "archived"):
            raise forms.ValidationError("Invalid status.")
        return status


class WeldMarkForm(forms.Form):
    weld_number = forms.CharField(max_length=100, required=False)
    geometry_json = forms.CharField(widget=forms.Textarea, required=False)
    marks_json = forms.CharField(widget=forms.Textarea, required=False)
    attributes_json = forms.CharField(widget=forms.Textarea, required=False)

    def clean_geometry_json(self):
        raw = self.cleaned_data.get("geometry_json")
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON.")

    def clean_marks_json(self):
        raw = self.cleaned_data.get("marks_json")
        if not raw:
            return []
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON.")
        if not isinstance(data, list):
            raise forms.ValidationError("Must be a list of marks.")
        return data


class WeldAttributeForm(forms.ModelForm):
    class Meta:
        model = models.WeldAttribute
        fields = ["weld", "name", "value"]


class WeldMaterialForm(forms.ModelForm):
    class Meta:
        model = models.WeldMaterial
        fields = ["weld", "material", "heat_number"]


class WeldConsumableForm(forms.ModelForm):
    class Meta:
        model = models.WeldConsumable
        fields = ["weld", "consumable", "batch"]


class VisualInspectionForm(forms.ModelForm):
    class Meta:
        model = models.VisualInspection
        fields = ["weld", "stage", "result", "notes", "inspector"]

    def clean_stage(self):
        stage = self.cleaned_data["stage"]
        if stage not in ("fit_up", "during_weld", "post_weld"):
            raise forms.ValidationError("Invalid stage.")
        return stage

    def clean_result(self):
        result = self.cleaned_data["result"]
        if result not in ("pass", "fail", "rework"):
            raise forms.ValidationError("Invalid result.")
        return result
