from django import forms

from . import models
from apps.projects import models as project_models


class DocumentForm(forms.ModelForm):
    class Meta:
        model = models.Document
        fields = ["project", "equipment", "type", "title", "status"]

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status not in ("active", "archived"):
            raise forms.ValidationError("Invalid status.")
        return status

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["equipment"].required = False
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

    def clean(self):
        cleaned = super().clean()
        project = cleaned.get("project")
        equipment = cleaned.get("equipment")
        if project and equipment and equipment.project_id != project.id:
            self.add_error("equipment", "Equipment does not belong to the project.")
        return cleaned


class DocumentRevisionForm(forms.ModelForm):
    upload = forms.FileField(required=False)

    class Meta:
        model = models.DocumentRevision
        fields = ["document", "revision", "file_path", "status"]
        widgets = {
            "file_path": forms.HiddenInput(),
            "status": forms.HiddenInput(),
        }

    def clean_status(self):
        status = self.cleaned_data.get("status") or "draft"
        if status not in ("draft", "in_review", "approved", "rejected", "archived"):
            raise forms.ValidationError("Invalid status.")
        return status


class DocumentApprovalForm(forms.ModelForm):
    class Meta:
        model = models.DocumentApproval
        fields = ["document_revision", "approver", "status"]
        widgets = {
            "document_revision": forms.HiddenInput(),
            "status": forms.HiddenInput(),
        }

    def clean_status(self):
        status = self.cleaned_data.get("status") or "pending"
        if status not in ("pending", "approved", "rejected"):
            raise forms.ValidationError("Invalid status.")
        return status


class DocumentSignatureForm(forms.ModelForm):
    signature_text = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = models.DocumentSignature
        fields = ["document_revision", "signer"]
        widgets = {
            "document_revision": forms.HiddenInput(),
        }

    def clean(self):
        cleaned = super().clean()
        text = cleaned.get("signature_text")
        if text:
            cleaned["signature_text"] = text.strip()
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        text = self.cleaned_data.get("signature_text") or ""
        instance.signature_blob = text.encode("utf-8") if text else b""
        if commit:
            instance.save()
        return instance
