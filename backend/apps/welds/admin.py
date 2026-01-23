from django.contrib import admin
from . import models


@admin.register(models.Drawing)
class DrawingAdmin(admin.ModelAdmin):
    list_display = ("code", "revision", "project", "status")
    search_fields = ("code",)


@admin.register(models.WeldMap)
class WeldMapAdmin(admin.ModelAdmin):
    list_display = ("project", "drawing", "status")


@admin.register(models.Weld)
class WeldAdmin(admin.ModelAdmin):
    list_display = ("number", "project", "status", "closed_at")
    search_fields = ("number",)


@admin.register(models.WeldMark)
class WeldMarkAdmin(admin.ModelAdmin):
    list_display = ("weld_map", "weld", "created_at")


@admin.register(models.WeldAttribute)
class WeldAttributeAdmin(admin.ModelAdmin):
    list_display = ("weld", "name", "value")


@admin.register(models.WeldAttributeCatalog)
class WeldAttributeCatalogAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "data_type", "status")


@admin.register(models.WeldMaterial)
class WeldMaterialAdmin(admin.ModelAdmin):
    list_display = ("weld", "material", "heat_number")


@admin.register(models.WeldConsumable)
class WeldConsumableAdmin(admin.ModelAdmin):
    list_display = ("weld", "consumable", "batch")


@admin.register(models.VisualInspection)
class VisualInspectionAdmin(admin.ModelAdmin):
    list_display = ("weld", "stage", "result", "inspector", "at")


@admin.register(models.WeldWpsAssignment)
class WeldWpsAssignmentAdmin(admin.ModelAdmin):
    list_display = ("weld", "wps", "status", "assigned_at")


@admin.register(models.WeldWelderAssignment)
class WeldWelderAssignmentAdmin(admin.ModelAdmin):
    list_display = ("weld", "welder", "status", "assigned_at")


@admin.register(models.WorkPack)
class WorkPackAdmin(admin.ModelAdmin):
    list_display = ("code", "project", "status")


@admin.register(models.Traveler)
class TravelerAdmin(admin.ModelAdmin):
    list_display = ("work_pack", "status")
