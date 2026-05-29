import uuid

from rest_framework import serializers

from apps.colleges.models import Branch, Department

from .models import AdmissionApplication, AdmissionCycle, AdmissionInquiry, MeritList


class AdmissionApplicationSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = AdmissionApplication
        fields = [
            'id',
            'college',
            'application_number',
            'first_name',
            'last_name',
            'email',
            'phone',
            'date_of_birth',
            'gender',
            'department',
            'department_name',
            'branch',
            'branch_name',
            'previous_school',
            'previous_percentage',
            'entrance_exam_score',
            'photo',
            'marksheet',
            'identity_proof',
            'other_documents',
            'status',
            'reviewed_by',
            'reviewed_at',
            'remarks',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'college',
            'application_number',
            'reviewed_by',
            'reviewed_at',
            'created_at',
            'updated_at',
        ]


class AdmissionApplicationWriteSerializer(serializers.ModelSerializer):
    application_number = serializers.CharField(max_length=50, required=False, allow_blank=True)

    class Meta:
        model = AdmissionApplication
        fields = [
            'application_number',
            'first_name',
            'last_name',
            'email',
            'phone',
            'date_of_birth',
            'gender',
            'department',
            'branch',
            'previous_school',
            'previous_percentage',
            'entrance_exam_score',
            'photo',
            'marksheet',
            'identity_proof',
            'other_documents',
            'status',
            'remarks',
        ]

    def validate(self, attrs):
        dept = attrs.get('department') or getattr(self.instance, 'department', None)
        branch = attrs.get('branch') or getattr(self.instance, 'branch', None)
        if dept and branch:
            if branch.department_id != dept.id:
                raise serializers.ValidationError({'branch': 'Branch must belong to the selected department.'})
            attrs['college'] = dept.college
        return attrs

    def validate_department(self, dept: Department):
        user = self.context['request'].user
        if user.role != 'SUPER_ADMIN' and getattr(user, 'college_id', None):
            if dept.college_id != user.college_id:
                raise serializers.ValidationError('Invalid department.')
        return dept

    def validate_branch(self, branch: Branch):
        user = self.context['request'].user
        if user.role != 'SUPER_ADMIN' and getattr(user, 'college_id', None):
            if branch.college_id != user.college_id:
                raise serializers.ValidationError('Invalid branch.')
        return branch

    def create(self, validated_data):
        num = (validated_data.get('application_number') or '').strip()
        if not num:
            validated_data['application_number'] = f'APP-{uuid.uuid4().hex[:12].upper()}'
        return super().create(validated_data)


class AdmissionCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionCycle
        fields = ['id', 'college', 'name', 'academic_year', 'start_date', 'end_date', 'is_active', 'created_at']
        read_only_fields = ['id', 'college', 'created_at']


class AdmissionInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionInquiry
        fields = [
            'id',
            'college',
            'name',
            'email',
            'phone',
            'source',
            'status',
            'department',
            'notes',
            'assigned_to',
            'application',
            'created_at',
        ]
        read_only_fields = ['id', 'college', 'assigned_to', 'created_at']


class MeritListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeritList
        fields = [
            'id',
            'college',
            'cycle',
            'title',
            'department',
            'published_at',
            'is_published',
            'created_at',
        ]
        read_only_fields = ['id', 'college', 'published_at', 'created_at']
