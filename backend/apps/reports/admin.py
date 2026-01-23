from django.contrib import admin
from . import models


@admin.register(models.Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("project", "type")


@admin.register(models.Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ("project",)


@admin.register(models.ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = ("type", "status", "created_at")


@admin.register(models.ImportError)
class ImportErrorAdmin(admin.ModelAdmin):
    list_display = ("job", "row_number", "message")
