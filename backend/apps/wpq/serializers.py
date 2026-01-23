from rest_framework import serializers
from . import models

class WelderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Welder
        fields = '__all__'


class WpqSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Wpq
        fields = '__all__'


class WpqProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WpqProcess
        fields = '__all__'


class WpqTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WpqTest
        fields = '__all__'


class ContinuityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContinuityLog
        fields = '__all__'


class ExpiryAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExpiryAlert
        fields = '__all__'


class WelderContinuitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WelderContinuity
        fields = '__all__'

