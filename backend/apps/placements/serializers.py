from rest_framework import serializers

from apps.students.models import Student

from .models import Company, JobPosting, PlacementApplication


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id',
            'college',
            'name',
            'industry',
            'website',
            'logo',
            'description',
            'contact_person',
            'contact_email',
            'contact_phone',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'created_at', 'updated_at']


class JobPostingSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = JobPosting
        fields = [
            'id',
            'college',
            'company',
            'company_name',
            'title',
            'description',
            'requirements',
            'salary_range',
            'job_type',
            'location',
            'openings',
            'application_deadline',
            'status',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'created_at', 'updated_at']


class JobPostingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = [
            'company',
            'title',
            'description',
            'requirements',
            'salary_range',
            'job_type',
            'location',
            'openings',
            'application_deadline',
            'status',
            'is_active',
        ]

    def validate_company(self, company: Company):
        req = self.context.get('request')
        if req and req.user.role == 'ADMIN' and getattr(req.user, 'college_id', None):
            if company.college_id != req.user.college_id:
                raise serializers.ValidationError('Invalid company.')
        return company

    def create(self, validated_data):
        company = validated_data['company']
        validated_data['college'] = company.college
        return super().create(validated_data)


class PlacementApplicationSerializer(serializers.ModelSerializer):
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = PlacementApplication
        fields = [
            'id',
            'college',
            'student',
            'student_enrollment',
            'job',
            'job_title',
            'status',
            'resume',
            'cover_letter',
            'applied_at',
            'interview_date',
            'offer_letter',
            'package_offered',
            'remarks',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class PlacementApplicationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementApplication
        fields = ['student', 'job', 'resume', 'cover_letter']

    def validate_job(self, job: JobPosting):
        if job.status != 'OPEN':
            raise serializers.ValidationError('Job is not accepting applications.')
        if not job.is_active or job.is_deleted:
            raise serializers.ValidationError('Invalid job.')
        return job

    def validate_student(self, student: Student):
        req = self.context.get('request')
        if req and req.user.role == 'STUDENT':
            try:
                profile = req.user.student_profile
            except Student.DoesNotExist as exc:
                raise serializers.ValidationError('Student profile required.') from exc
            if student.pk != profile.pk:
                raise serializers.ValidationError('Invalid student.')
        if req and req.user.role == 'ADMIN' and getattr(req.user, 'college_id', None):
            if student.college_id != req.user.college_id:
                raise serializers.ValidationError('Invalid student.')
        return student

    def validate(self, attrs):
        student = attrs['student']
        job = attrs['job']
        if student.college_id != job.college_id:
            raise serializers.ValidationError('Student and job must belong to the same college.')
        attrs['college'] = student.college
        return attrs
