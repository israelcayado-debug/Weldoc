from rest_framework import serializers
from . import models

class ValidationRuleSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ValidationRuleSet
        fields = '__all__'


class ValidationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ValidationRule
        fields = '__all__'


class ValidationRuleSetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ValidationRuleSetItem
        fields = '__all__'


class NdeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NdeRequest
        fields = '__all__'


class NdeResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NdeResult
        fields = '__all__'


class PwhtRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PwhtRecord
        fields = '__all__'


class PressureTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PressureTest
        fields = '__all__'


class NdeSamplingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NdeSamplingRule
        fields = '__all__'

