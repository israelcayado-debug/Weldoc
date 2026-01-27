from django import forms

from . import models


PROJECT_STATUS = ("active", "archived")
UNITS = ("metric", "imperial")


class ClientForm(forms.ModelForm):
    class Meta:
        model = models.Client
        fields = ["name", "tax_id", "status"]

    def clean_status(self):
        status = (self.cleaned_data.get("status") or "active").strip()
        if status not in PROJECT_STATUS:
            raise forms.ValidationError("Invalid status.")
        return status


class ProjectForm(forms.ModelForm):
    standard_set_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Separate standards with commas (e.g., ASME IX, ISO 15614-1).",
    )
    equipment_name = forms.CharField(required=False, label="Equipment name", max_length=200)
    equipment_fabrication_code = forms.CharField(
        required=False, label="Fabrication code", max_length=100
    )

    class Meta:
        model = models.Project
        fields = ["client", "name", "code", "purchase_order", "units", "status"]

    def __init__(self, *args, **kwargs):
        self.require_equipment = bool(kwargs.pop("require_equipment", False))
        super().__init__(*args, **kwargs)
        self.fields["client"].required = True
        self.fields["code"].label = "Project number"
        self.fields["code"].help_text = "Must be 8 digits."
        self.fields["purchase_order"].label = "Customer Purchase Order"
        self.fields["purchase_order"].required = True
        if self.instance and self.instance.standard_set:
            self.fields["standard_set_text"].initial = ", ".join(
                [str(item) for item in self.instance.standard_set]
            )
        if not self.require_equipment:
            self.fields.pop("equipment_name", None)
            self.fields.pop("equipment_fabrication_code", None)

    def clean_units(self):
        units = (self.cleaned_data.get("units") or "metric").strip()
        if units not in UNITS:
            raise forms.ValidationError("Invalid unit.")
        return units

    def clean_code(self):
        code = (self.cleaned_data.get("code") or "").strip()
        if not code:
            raise forms.ValidationError("Project number is required.")
        if not (code.isdigit() and len(code) == 8):
            raise forms.ValidationError("Project number must be 8 digits.")
        return code

    def clean_status(self):
        status = (self.cleaned_data.get("status") or "active").strip()
        if status not in PROJECT_STATUS:
            raise forms.ValidationError("Invalid status.")
        return status

    def clean_purchase_order(self):
        value = (self.cleaned_data.get("purchase_order") or "").strip()
        if not value:
            raise forms.ValidationError("Purchase Order is required.")
        return value

    def clean_standard_set_text(self):
        value = (self.cleaned_data.get("standard_set_text") or "").strip()
        if not value:
            return []
        items = [item.strip() for item in value.split(",") if item.strip()]
        return items

    def clean(self):
        cleaned = super().clean()
        if self.require_equipment:
            name = (cleaned.get("equipment_name") or "").strip()
            code = (cleaned.get("equipment_fabrication_code") or "").strip()
            if not name:
                self.add_error("equipment_name", "Equipment name is required.")
            if not code:
                self.add_error("equipment_fabrication_code", "Fabrication code is required.")
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.standard_set = self.cleaned_data.get("standard_set_text") or []
        if commit:
            instance.save()
        return instance


class ProjectEquipmentForm(forms.ModelForm):
    class Meta:
        model = models.ProjectEquipment
        fields = ["project", "name", "fabrication_code", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = "Equipment name"
        self.fields["fabrication_code"].label = "Fabrication code"

    def clean_status(self):
        status = (self.cleaned_data.get("status") or "active").strip()
        if status not in PROJECT_STATUS:
            raise forms.ValidationError("Invalid status.")
        return status
