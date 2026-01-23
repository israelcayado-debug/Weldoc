from django.contrib import admin
from . import models


@admin.register(models.Welder)
class WelderAdmin(admin.ModelAdmin):
    list_display = ("name", "employer", "status")
    search_fields = ("name", "employer")


@admin.register(models.Wpq)
class WpqAdmin(admin.ModelAdmin):
    list_display = ("code", "standard", "status", "welder")
    search_fields = ("code",)


@admin.register(models.WpqProcess)
class WpqProcessAdmin(admin.ModelAdmin):
    list_display = ("wpq", "process", "positions", "thickness_range")


@admin.register(models.WpqTest)
class WpqTestAdmin(admin.ModelAdmin):
    list_display = ("wpq", "test_type", "result")


@admin.register(models.ContinuityLog)
class ContinuityLogAdmin(admin.ModelAdmin):
    list_display = ("welder", "weld", "date", "process")


@admin.register(models.ExpiryAlert)
class ExpiryAlertAdmin(admin.ModelAdmin):
    list_display = ("welder", "wpq", "due_date", "sent_at")


@admin.register(models.WelderContinuity)
class WelderContinuityAdmin(admin.ModelAdmin):
    list_display = ("welder", "status", "last_activity_date", "continuity_due_date")
