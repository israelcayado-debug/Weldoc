import uuid
from django.db import models


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=320, unique=True)
    status = models.CharField(max_length=30, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "User"


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    scope = models.CharField(max_length=30, default="global")

    class Meta:
        db_table = "Role"


class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "Permission"


class UserRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    role = models.ForeignKey("users.Role", on_delete=models.CASCADE)

    class Meta:
        db_table = "UserRole"
        constraints = [
            models.UniqueConstraint(fields=["user", "role"], name="user_role_unique")
        ]


class RolePermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey("users.Role", on_delete=models.CASCADE)
    permission = models.ForeignKey("users.Permission", on_delete=models.CASCADE)

    class Meta:
        db_table = "RolePermission"
        constraints = [
            models.UniqueConstraint(fields=["role", "permission"], name="role_permission_unique")
        ]


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, null=True)
    recipient = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True)
    channel = models.CharField(max_length=20, default="email")
    subject = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(max_length=30, default="queued")
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Notification"
