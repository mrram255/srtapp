from rest_framework import serializers

from .models import Student, StudentDocument, StudentSemesterRecord, StudentDocumentVerification


class StudentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.year', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id',
            'user',
            'user_name',
            'user_email',
            'college',
            'enrollment_number',
            'roll_number',
            'department',
            'department_name',
            'branch',
            'branch_name',
            'academic_year',
            'academic_year_name',
            'semester',
            'section',
            'batch_year',
            'date_of_birth',
            'gender',
            'blood_group',
            'nationality',
            'religion',
            'category',
            'address',
            'city',
            'state',
            'pincode',
            'emergency_contact',
            'emergency_contact_name',
            'admission_date',
            'admission_type',
            'previous_education',
            'previous_percentage',
            'photo',
            'signature',
            'id_card',
            'documents',
            'student_status',
            'abc_id',
            'digilocker_id',
            'hostel_resident',
            'transport_user',
            'library_card_number',
            'admission_number',
            'university_roll_number',
            'caste',
            'sub_category',
            'domicile_state',
            'mother_tongue',
            'identification_mark',
            'family_details',
            'education_details',
            'permanent_address',
            'correspondence_address',
            'is_address_same',
            'mentor',
            'is_active',
            'graduation_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'user', 'created_at', 'updated_at']


class StudentSelfUpdateSerializer(serializers.ModelSerializer):
    """Fields a student may update on their own profile."""

    class Meta:
        model = Student
        fields = [
            'blood_group',
            'address',
            'city',
            'state',
            'pincode',
            'emergency_contact',
            'emergency_contact_name',
            'photo',
            'documents',
        ]


class StudentCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=12)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = [
            'email',
            'password',
            'first_name',
            'last_name',
            'phone',
            'enrollment_number',
            'roll_number',
            'department',
            'branch',
            'academic_year',
            'semester',
            'section',
            'batch_year',
            'date_of_birth',
            'gender',
            'blood_group',
            'nationality',
            'religion',
            'category',
            'address',
            'city',
            'state',
            'pincode',
            'emergency_contact',
            'emergency_contact_name',
            'admission_date',
            'admission_type',
            'previous_education',
            'previous_percentage',
            'student_status',
            'abc_id',
            'digilocker_id',
            'hostel_resident',
            'transport_user',
            'library_card_number',
            'admission_number',
            'university_roll_number',
            'caste',
            'sub_category',
            'domicile_state',
            'mother_tongue',
            'identification_mark',
            'family_details',
            'education_details',
            'permanent_address',
            'correspondence_address',
            'is_address_same',
        ]

    def validate(self, data):
        dept = data['department']
        branch = data['branch']
        if branch.department_id != dept.id:
            raise serializers.ValidationError({'branch': 'Branch must belong to the selected department.'})
        ay = data.get('academic_year')
        if ay is not None and ay.college_id != dept.college_id:
            raise serializers.ValidationError(
                {'academic_year': 'Academic year must belong to the same college as the department.'}
            )
        return data

    def create(self, validated_data):
        from apps.accounts.models import User

        college = validated_data['department'].college

        user_data = {
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'phone': validated_data.pop('phone'),
            'role': 'STUDENT',
            'college': college,
        }

        user = User.objects.create_user(**user_data)
        validated_data['user'] = user
        validated_data['college'] = college

        return Student.objects.create(**validated_data)


class StudentBulkImportSerializer(serializers.Serializer):
    file = serializers.FileField()


class StudentDocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True, required=False)
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.full_name', read_only=True)

    class Meta:
        model = StudentDocument
        fields = [
            'id',
            'student',
            'student_name',
            'document_type',
            'file_url',
            'file_name',
            'file_size',
            'mime_type',
            'is_verified',
            'verified_by',
            'verified_by_name',
            'verified_at',
            'remarks',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentDashboardSerializer(serializers.Serializer):
    """Dashboard payload for student home."""

    student_id = serializers.UUIDField()
    name = serializers.CharField()
    enrollment_number = serializers.CharField()
    department = serializers.CharField()
    semester = serializers.IntegerField()
    section = serializers.CharField()
    attendance_percentage = serializers.FloatField()
    pending_assignments = serializers.IntegerField()
    upcoming_exams = serializers.IntegerField()
    fee_status = serializers.CharField()
    recent_notifications = serializers.ListField()


class StudentSemesterRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSemesterRecord
        fields = [
            'id', 'student', 'semester_number', 'academic_year_label',
            'sgpa', 'cgpa', 'total_credits_earned',
            'attendance_percentage', 'status', 'promoted_to_next',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentDocumentVerificationSerializer(serializers.ModelSerializer):
    verified_by_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentDocumentVerification
        fields = [
            'id', 'student', 'document_type', 'status',
            'verified_by', 'verified_by_name', 'verified_at',
            'remarks', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'verified_by_name']

    def get_verified_by_name(self, obj):
        return obj.verified_by.get_full_name() if obj.verified_by else None
