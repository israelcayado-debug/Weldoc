from django import forms

from . import models


class WpsForm(forms.ModelForm):
    class Meta:
        model = models.Wps
        fields = ["project", "code", "standard", "impact_test", "status"]

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status not in ("draft", "in_review", "approved", "archived"):
            raise forms.ValidationError("Invalid status.")
        return status


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
