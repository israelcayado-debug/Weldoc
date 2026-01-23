from django.contrib import admin
from . import models


@admin.register(models.IntegrationEndpoint)
class IntegrationEndpointAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "url")


@admin.register(models.IntegrationEvent)
class IntegrationEventAdmin(admin.ModelAdmin):
    list_display = ("integration", "event_type", "status", "created_at")
