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

    def validate_code(self, value):
        value = (value or "").strip()
        if not (value.isdigit() and len(value) == 8):
            raise serializers.ValidationError("Project number must be 8 digits.")
        return value

    def validate_purchase_order(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Purchase Order requerido.")
        return value


class ProjectUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProjectUser
        fields = '__all__'


class ProjectEquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProjectEquipment
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

