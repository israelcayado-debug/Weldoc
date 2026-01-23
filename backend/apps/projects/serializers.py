from rest_framework import serializers
from . import models

class SchemaVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SchemaVersion
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Client
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = '__all__'


class ProjectUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProjectUser
        fields = '__all__'


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AuditLog
        fields = '__all__'


class AuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AuditEvent
        fields = '__all__'


class NumberingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NumberingRule
        fields = '__all__'

