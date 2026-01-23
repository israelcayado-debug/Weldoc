from django.contrib import admin
from . import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "status", "created_at")
    search_fields = ("name", "email")


@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "scope")
    search_fields = ("name",)


@admin.register(models.Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("code",)
    search_fields = ("code",)


@admin.register(models.UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role")


@admin.register(models.RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "permission")


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("subject", "recipient", "channel", "status", "created_at")
    search_fields = ("subject",)
