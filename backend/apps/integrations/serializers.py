from rest_framework import serializers
from . import models

class IntegrationEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IntegrationEndpoint
        fields = '__all__'


class IntegrationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IntegrationEvent
        fields = '__all__'

