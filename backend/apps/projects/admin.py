from django.contrib import admin
from . import models


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "tax_id", "status")
    search_fields = ("name", "tax_id")


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "purchase_order", "status", "units")
    search_fields = ("name", "code", "purchase_order")


@admin.register(models.ProjectUser)
class ProjectUserAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "role")


@admin.register(models.ProjectEquipment)
class ProjectEquipmentAdmin(admin.ModelAdmin):
    list_display = ("project", "name", "fabrication_code", "status")
    search_fields = ("name", "fabrication_code")


@admin.register(models.AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("entity", "action", "user", "at")


@admin.register(models.AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("event_code", "entity", "user", "at")


@admin.register(models.NumberingRule)
class NumberingRuleAdmin(admin.ModelAdmin):
    list_display = ("project", "type", "pattern", "next_seq")


@admin.register(models.SchemaVersion)
class SchemaVersionAdmin(admin.ModelAdmin):
    list_display = ("version", "name", "applied_at")
