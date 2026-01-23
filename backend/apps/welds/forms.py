from django import forms

from . import models


class WeldForm(forms.ModelForm):
    class Meta:
        model = models.Weld
        fields = ["project", "drawing", "number", "status"]

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status not in ("planned", "in_progress", "completed", "repair"):
            raise forms.ValidationError("Estado no valido.")
        return status


class DrawingForm(forms.ModelForm):
    upload = forms.FileField(required=False)

    class Meta:
        model = models.Drawing
        fields = ["project", "code", "revision", "file_path", "status"]
        widgets = {
            "file_path": forms.HiddenInput(),
        }

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status not in ("active", "archived"):
            raise forms.ValidationError("Estado no valido.")
        return status


class WeldMapForm(forms.ModelForm):
    class Meta:
        model = models.WeldMap
        fields = ["project", "drawing", "status"]

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status not in ("active", "archived"):
            raise forms.ValidationError("Estado no valido.")
        return status
