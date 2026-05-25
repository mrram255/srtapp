from django.utils import timezone
from rest_framework import serializers

from .models import GeneratedReport, ReportTemplate


class ReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = [
            'id',
            'college',
            'name',
            'report_type',
            'description',
            'parameters',
            'template_file',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'created_at', 'updated_at']


class GeneratedReportSerializer(serializers.ModelSerializer):
    generated_by_email = serializers.EmailField(source='generated_by.email', read_only=True)

    class Meta:
        model = GeneratedReport
        fields = [
            'id',
            'college',
            'template',
            'name',
            'parameters',
            'file_url',
            'file_size',
            'status',
            'generated_by',
            'generated_by_email',
            'started_at',
            'completed_at',
            'error_message',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class GeneratedReportWriteSerializer(serializers.ModelSerializer):
    parameters = serializers.JSONField(required=False)

    class Meta:
        model = GeneratedReport
        fields = ['template', 'name', 'parameters']

    def validate_template(self, template: ReportTemplate):
        req = self.context['request']
        if getattr(template, 'is_deleted', False) or not template.is_active:
            raise serializers.ValidationError('Invalid template.')
        if req.user.role == 'ADMIN' and getattr(req.user, 'college_id', None):
            if template.college_id != req.user.college_id:
                raise serializers.ValidationError('Invalid template.')
        return template

    def create(self, validated_data):
        template = validated_data['template']
        params = validated_data.get('parameters')
        if params is None:
            params = {}
        user = self.context['request'].user
        return GeneratedReport.objects.create(
            template=template,
            name=validated_data['name'],
            parameters=params,
            generated_by=user,
            college=template.college,
            status='PENDING',
            started_at=timezone.now(),
        )
