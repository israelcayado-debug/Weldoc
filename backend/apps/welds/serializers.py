from rest_framework import serializers
from . import models

class DrawingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Drawing
        fields = '__all__'


class WeldMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WeldMap
        fields = '__all__'


class WeldSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Weld
        fields = '__all__'


class WeldMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WeldMark
        fields = '__all__'


class WeldAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WeldAttribute
        fields = '__all__'


class WeldAttributeCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WeldAttributeCatalog
        fields = '__all__'


class WeldMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WeldMaterial
        fields = '__all__'


class WeldConsumableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WeldConsumable
        fields = '__all__'


class VisualInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.VisualInspection
        fields = '__all__'


class WeldWpsAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WeldWpsAssignment
        fields = '__all__'


class WeldWelderAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WeldWelderAssignment
        fields = '__all__'


class WorkPackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkPack
        fields = '__all__'


class TravelerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Traveler
        fields = '__all__'

