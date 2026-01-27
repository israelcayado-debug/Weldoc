from django import forms

from . import models


class NdeRequestForm(forms.ModelForm):
    class Meta:
        model = models.NdeRequest
        fields = ["project", "weld", "method", "status", "requested_by"]

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status not in ("requested", "in_progress", "completed", "cancelled"):
            raise forms.ValidationError("Invalid status.")
        return status


class NdeResultForm(forms.ModelForm):
    upload = forms.FileField(required=False)

    class Meta:
        model = models.NdeResult
        fields = ["nde_request", "result", "defect_type", "report_path", "inspector"]
        widgets = {
            "report_path": forms.HiddenInput(),
        }

    def clean_result(self):
        result = self.cleaned_data["result"]
        if result not in ("accept", "reject", "repair"):
            raise forms.ValidationError("Invalid result.")
        return result


class PwhtRecordForm(forms.ModelForm):
    upload = forms.FileField(required=False)

    class Meta:
        model = models.PwhtRecord
        fields = ["weld", "cycle_params_json", "result", "report_path"]
        widgets = {
            "report_path": forms.HiddenInput(),
        }

    def clean_result(self):
        result = self.cleaned_data["result"]
        if result not in ("pass", "fail", "rework"):
            raise forms.ValidationError("Invalid result.")
        return result


class PressureTestForm(forms.ModelForm):
    upload = forms.FileField(required=False)

    class Meta:
        model = models.PressureTest
        fields = [
            "project",
            "line_id",
            "test_type",
            "pressure",
            "duration_min",
            "result",
            "report_path",
        ]
        widgets = {
            "report_path": forms.HiddenInput(),
        }

    def clean_result(self):
        result = self.cleaned_data["result"]
        if result not in ("pass", "fail", "retest"):
            raise forms.ValidationError("Invalid result.")
        return result
