from rest_framework import serializers

from .models import CertificateIssue, CertificateRequest, CertificateTemplate
from .services import CertificateService


class CertificateTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateTemplate
        fields = [
            'id',
            'college',
            'name',
            'code',
            'description',
            'certificate_type',
            'template_file',
            'html_body',
            'header_image',
            'footer_image',
            'variables',
            'requires_approval',
            'auto_generate',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CertificateIssueSerializer(serializers.ModelSerializer):
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.get_full_name', read_only=True)

    class Meta:
        model = CertificateIssue
        fields = [
            'id',
            'request',
            'certificate_number',
            'student',
            'student_enrollment',
            'student_name',
            'template',
            'template_name',
            'issued_by',
            'issued_by_name',
            'status',
            'issued_at',
            'download_url',
            'pdf_url',
            'qr_verification_url',
            'verification_code',
            'blockchain_hash',
            'qr_payload',
            'data_snapshot',
            'valid_until',
            'is_revoked',
            'revoked_reason',
            'download_count',
            'remarks',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'student_enrollment',
            'student_name',
            'template_name',
            'issued_by_name',
            'certificate_number',
            'verification_code',
            'blockchain_hash',
            'qr_payload',
            'pdf_url',
            'download_url',
            'qr_verification_url',
            'data_snapshot',
            'download_count',
            'created_at',
            'updated_at',
        ]


class CertificateIssueCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateIssue
        fields = ['student', 'template', 'remarks']

    def create(self, validated_data):
        request = self.context['request']
        return CertificateService.issue_direct(
            student=validated_data['student'],
            template=validated_data['template'],
            issued_by=request.user,
            remarks=validated_data.get('remarks', ''),
        )


class CertificateRequestSerializer(serializers.ModelSerializer):
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    issue_id = serializers.SerializerMethodField()

    class Meta:
        model = CertificateRequest
        fields = [
            'id',
            'request_number',
            'student',
            'student_enrollment',
            'student_name',
            'template',
            'template_name',
            'requested_by',
            'requested_by_name',
            'purpose',
            'number_of_copies',
            'status',
            'reviewed_by',
            'reviewed_by_name',
            'reviewed_at',
            'review_remarks',
            'rejected_reason',
            'generated_at',
            'fee_amount',
            'fee_paid',
            'remarks',
            'issue_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'request_number',
            'student_enrollment',
            'student_name',
            'template_name',
            'requested_by_name',
            'reviewed_by',
            'reviewed_by_name',
            'reviewed_at',
            'review_remarks',
            'rejected_reason',
            'generated_at',
            'status',
            'issue_id',
            'created_at',
            'updated_at',
        ]

    def get_issue_id(self, obj):
        try:
            return str(obj.certificate_issue.id)
        except CertificateIssue.DoesNotExist:
            return None


class CertificateRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateRequest
        fields = ['student', 'template', 'purpose', 'number_of_copies', 'fee_amount', 'fee_paid', 'remarks']

    def validate(self, attrs):
        student = attrs['student']
        template = attrs['template']
        if student.college_id != template.college_id:
            raise serializers.ValidationError({'template': 'Template must belong to the student college.'})
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        if user.role == 'STUDENT' and validated_data['student'].user_id != user.id:
            raise serializers.ValidationError({'student': 'You can only request for yourself.'})
        return CertificateService.request_certificate(
            student=validated_data['student'],
            template=validated_data['template'],
            requested_by=user,
            purpose=validated_data.get('purpose', ''),
            number_of_copies=validated_data.get('number_of_copies', 1),
            fee_amount=validated_data.get('fee_amount', 0),
            fee_paid=validated_data.get('fee_paid', False),
            remarks=validated_data.get('remarks', ''),
        )


class CertificateBulkIssueSerializer(serializers.Serializer):
    request_ids = serializers.ListField(child=serializers.UUIDField(), min_length=1)


class CertificateBulkStudentsSerializer(serializers.Serializer):
    student_ids = serializers.ListField(child=serializers.UUIDField(), min_length=1)
    template_id = serializers.UUIDField()


class CertificateRevokeSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default='')
