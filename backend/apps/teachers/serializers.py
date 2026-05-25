from rest_framework import serializers

from .models import Teacher, TeacherSubjectAssignment


class TeacherSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Teacher
        fields = [
            'id',
            'user',
            'user_name',
            'user_email',
            'college',
            'employee_id',
            'department',
            'department_name',
            'designation',
            'specialization',
            'qualification',
            'experience_years',
            'office_room',
            'office_hours',
            'resume',
            'documents',
            'joining_date',
            'employment_type',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'college', 'created_at', 'updated_at']


class TeacherCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=12)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)

    class Meta:
        model = Teacher
        fields = [
            'email',
            'password',
            'first_name',
            'last_name',
            'phone',
            'employee_id',
            'department',
            'designation',
            'specialization',
            'qualification',
            'experience_years',
            'office_room',
            'office_hours',
            'joining_date',
            'employment_type',
        ]

    def validate(self, data):
        dept = data['department']
        data['college'] = dept.college
        return data

    def create(self, validated_data):
        from apps.accounts.models import User

        college = validated_data['college']
        department = validated_data['department']

        user_data = {
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'phone': validated_data.pop('phone'),
            'role': 'TEACHER',
            'college': college,
            'department': department,
        }

        user = User.objects.create_user(**user_data)
        validated_data['user'] = user

        return Teacher.objects.create(**validated_data)


class TeacherSubjectAssignmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.year', read_only=True)

    class Meta:
        model = TeacherSubjectAssignment
        fields = [
            'id',
            'teacher',
            'teacher_name',
            'subject',
            'subject_name',
            'subject_code',
            'semester',
            'section',
            'academic_year',
            'academic_year_name',
            'is_primary',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        teacher = data['teacher']
        subject = data['subject']
        academic_year = data['academic_year']

        if subject.college_id != teacher.college_id or subject.department_id != teacher.department_id:
            raise serializers.ValidationError(
                {'subject': 'Subject must belong to the same college and department as the teacher.'}
            )
        if academic_year.college_id != teacher.college_id:
            raise serializers.ValidationError(
                {'academic_year': 'Academic year must belong to the same college as the teacher.'}
            )
        return data


class TeacherDashboardSerializer(serializers.Serializer):
    teacher_id = serializers.UUIDField()
    name = serializers.CharField()
    employee_id = serializers.CharField()
    department = serializers.CharField()
    designation = serializers.CharField()
    today_classes = serializers.IntegerField()
    pending_attendance = serializers.IntegerField()
    pending_assignments = serializers.IntegerField()
    total_students = serializers.IntegerField()
    recent_notifications = serializers.ListField()
