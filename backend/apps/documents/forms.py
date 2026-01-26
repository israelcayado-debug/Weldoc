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
            raise forms.ValidationError("Estado no valido.")
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
            raise forms.ValidationError("Estado no valido.")
        return status


class DocumentSignatureForm(forms.ModelForm):
    signature_text = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = models.DocumentSignature
        fields = ["document_revision", "signer", "signature_blob"]
        widgets = {
            "document_revision": forms.HiddenInput(),
            "signature_blob": forms.HiddenInput(),
        }

    def clean(self):
        cleaned = super().clean()
        text = cleaned.get("signature_text")
        if text:
            cleaned["signature_blob"] = text.encode("utf-8")
        return cleaned
