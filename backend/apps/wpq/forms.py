from django import forms

from . import models


class WpqForm(forms.ModelForm):
    class Meta:
        model = models.Wpq
        fields = ["welder", "code", "standard", "status"]

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status not in ("draft", "in_review", "approved", "archived"):
            raise forms.ValidationError("Invalid status.")
        return status
