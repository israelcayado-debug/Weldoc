from django import forms

from . import models


class WpsForm(forms.ModelForm):
    class Meta:
        model = models.Wps
        fields = ["project", "code", "standard", "status"]

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status not in ("draft", "in_review", "approved", "archived"):
            raise forms.ValidationError("Estado no valido.")
        return status
