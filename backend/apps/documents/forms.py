from django import forms

from . import models


class DocumentForm(forms.ModelForm):
    class Meta:
        model = models.Document
        fields = ["project", "type", "title", "status"]

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status not in ("active", "archived"):
            raise forms.ValidationError("Estado no valido.")
        return status
