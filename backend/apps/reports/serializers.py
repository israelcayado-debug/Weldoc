from rest_framework import serializers
from . import models

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Report
        fields = '__all__'


class DossierSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Dossier
        fields = '__all__'


class ImportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ImportJob
        fields = '__all__'


class ImportErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ImportError
        fields = '__all__'


class ProgressReportSerializer(serializers.Serializer):
    project_id = serializers.UUIDField()
    total_welds = serializers.IntegerField()
    by_status = serializers.DictField(child=serializers.IntegerField())


class ExpiringWelderSerializer(serializers.Serializer):
    welder_id = serializers.UUIDField()
    name = serializers.CharField()
    due_date = serializers.DateField(allow_null=True, required=False)


class OutOfContinuityWelderSerializer(serializers.Serializer):
    welder_id = serializers.UUIDField()
    name = serializers.CharField()
    last_activity = serializers.DateField(allow_null=True, required=False)


class ExpiryReportSerializer(serializers.Serializer):
    project_id = serializers.UUIDField()
    expiring_30_days = ExpiringWelderSerializer(many=True)
    out_of_continuity = OutOfContinuityWelderSerializer(many=True)


class ExportWeldingListRequestSerializer(serializers.Serializer):
    project_id = serializers.UUIDField()
    filters = serializers.DictField(required=False)


class ExportQualificationsRequestSerializer(serializers.Serializer):
    project_id = serializers.UUIDField()
    type = serializers.ChoiceField(choices=["WPS", "WPQ"])


class ExportDossierRequestSerializer(serializers.Serializer):
    project_id = serializers.UUIDField()
    include = serializers.ListField(child=serializers.CharField(), required=False)


class ExportStatusSerializer(serializers.Serializer):
    export_id = serializers.UUIDField()
    status = serializers.CharField()
    file_path = serializers.CharField(allow_null=True, required=False)

