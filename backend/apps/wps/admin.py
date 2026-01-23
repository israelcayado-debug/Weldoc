from django.contrib import admin
from . import models


@admin.register(models.MaterialBase)
class MaterialBaseAdmin(admin.ModelAdmin):
    list_display = ("spec", "grade", "group_no")
    search_fields = ("spec", "grade", "group_no")


@admin.register(models.FillerMaterial)
class FillerMaterialAdmin(admin.ModelAdmin):
    list_display = ("spec", "classification", "group_no")
    search_fields = ("spec", "classification", "group_no")


@admin.register(models.JointType)
class JointTypeAdmin(admin.ModelAdmin):
    list_display = ("code",)
    search_fields = ("code",)


@admin.register(models.Wps)
class WpsAdmin(admin.ModelAdmin):
    list_display = ("code", "standard", "status", "project")
    search_fields = ("code",)


@admin.register(models.Pqr)
class PqrAdmin(admin.ModelAdmin):
    list_display = ("code", "standard", "status", "project")
    search_fields = ("code",)


@admin.register(models.WpsPqrLink)
class WpsPqrLinkAdmin(admin.ModelAdmin):
    list_display = ("wps", "pqr")


@admin.register(models.WpsVariable)
class WpsVariableAdmin(admin.ModelAdmin):
    list_display = ("wps", "name", "value")


@admin.register(models.PqrResult)
class PqrResultAdmin(admin.ModelAdmin):
    list_display = ("pqr", "test_type", "result")
