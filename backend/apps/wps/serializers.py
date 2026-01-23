from rest_framework import serializers
from . import models

class MaterialBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MaterialBase
        fields = '__all__'


class FillerMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FillerMaterial
        fields = '__all__'


class JointTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.JointType
        fields = '__all__'


class WpsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Wps
        fields = '__all__'


class PqrSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pqr
        fields = '__all__'


class WpsPqrLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WpsPqrLink
        fields = '__all__'


class WpsVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WpsVariable
        fields = '__all__'


class PqrResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PqrResult
        fields = '__all__'

