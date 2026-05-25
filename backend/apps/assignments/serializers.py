from rest_framework import serializers

from apps.teachers.models import Teacher

from .models import Assignment, AssignmentSubmission


class AssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id',
            'college',
            'title',
            'description',
            'subject',
            'subject_name',
            'teacher',
            'teacher_name',
            'department',
            'semester',
            'section',
            'max_marks',
            'due_date',
            'attachment',
            'status',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'created_at', 'updated_at']


class AssignmentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = [
            'title',
            'description',
            'subject',
            'teacher',
            'department',
            'semester',
            'section',
            'max_marks',
            'due_date',
            'attachment',
            'status',
        ]
        extra_kwargs = {
            'teacher': {'required': False},
            'department': {'required': False},
        }

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if user and user.role == 'TEACHER':
            try:
                teacher = Teacher.objects.select_related('department').get(user=user)
            except Teacher.DoesNotExist:
                raise serializers.ValidationError({'teacher': ['Teacher profile not found.']}) from None
            attrs['teacher'] = teacher
            attrs['department'] = teacher.department

        teacher = attrs.get('teacher')
        if teacher is None:
            raise serializers.ValidationError({'teacher': ['This field is required.']})

        attrs.setdefault('department', teacher.department)

        department = attrs['department']
        subject = attrs['subject']
        semester = attrs['semester']

        if teacher.department_id != department.id:
            raise serializers.ValidationError({'department': 'Department must match the teacher department.'})
        if subject.department_id != department.id:
            raise serializers.ValidationError({'department': 'Department must match the subject department.'})
        if subject.semester != semester:
            raise serializers.ValidationError({'semester': 'Semester must match the subject semester.'})
        if teacher.college_id != subject.college_id:
            raise serializers.ValidationError('Teacher and subject must belong to the same college.')

        attrs['college'] = teacher.college
        return attrs


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = [
            'id',
            'college',
            'assignment',
            'assignment_title',
            'student',
            'student_enrollment',
            'submission_text',
            'attachment',
            'submitted_at',
            'marks_obtained',
            'feedback',
            'status',
            'graded_by',
            'graded_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'created_at', 'updated_at']
