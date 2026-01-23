from django.contrib import admin
from . import models


@admin.register(models.ValidationRuleSet)
class ValidationRuleSetAdmin(admin.ModelAdmin):
    list_display = ("code", "standard", "applies_to", "status")
    search_fields = ("code",)


@admin.register(models.ValidationRule)
class ValidationRuleAdmin(admin.ModelAdmin):
    list_display = ("code", "applies_to", "severity", "status")
    search_fields = ("code",)


@admin.register(models.ValidationRuleSetItem)
class ValidationRuleSetItemAdmin(admin.ModelAdmin):
    list_display = ("ruleset", "rule", "sort_order")


@admin.register(models.NdeRequest)
class NdeRequestAdmin(admin.ModelAdmin):
    list_display = ("project", "weld", "method", "status", "requested_at")


@admin.register(models.NdeResult)
class NdeResultAdmin(admin.ModelAdmin):
    list_display = ("nde_request", "result", "defect_type")


@admin.register(models.PwhtRecord)
class PwhtRecordAdmin(admin.ModelAdmin):
    list_display = ("weld", "result")


@admin.register(models.PressureTest)
class PressureTestAdmin(admin.ModelAdmin):
    list_display = ("project", "line_id", "test_type", "result")


@admin.register(models.NdeSamplingRule)
class NdeSamplingRuleAdmin(admin.ModelAdmin):
    list_display = ("project", "method", "ratio")
