from rest_framework import serializers
from . import models

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = '__all__'


class DocumentRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocumentRevision
        fields = '__all__'


class DocumentApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocumentApproval
        fields = '__all__'


class DocumentSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocumentSignature
        fields = '__all__'

