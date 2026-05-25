from rest_framework import serializers

from .models import Course, Subject, Timetable


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id',
            'college',
            'name',
            'code',
            'description',
            'credits',
            'duration_hours',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'created_at', 'updated_at']


class SubjectSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = Subject
        fields = [
            'id',
            'college',
            'course',
            'course_name',
            'department',
            'name',
            'code',
            'semester',
            'credits',
            'theory_hours',
            'practical_hours',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'created_at', 'updated_at']


class TimetableSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True)

    class Meta:
        model = Timetable
        fields = [
            'id',
            'college',
            'subject',
            'subject_name',
            'teacher',
            'teacher_name',
            'department',
            'semester',
            'section',
            'day',
            'start_time',
            'end_time',
            'room_number',
            'academic_year',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'college', 'created_at', 'updated_at']


class TimetableWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = [
            'subject', 'teacher', 'department', 'semester',
            'section', 'day', 'start_time', 'end_time',
            'room_number', 'academic_year', 'is_active',
        ]

    def validate(self, attrs):
        subject = attrs.get('subject')
        teacher = attrs.get('teacher')
        department = attrs.get('department')
        academic_year = attrs.get('academic_year')

        if subject and teacher and subject.college_id != teacher.college_id:
            raise serializers.ValidationError('Subject and teacher must belong to the same college.')
        if subject and department and subject.department_id != department.id:
            raise serializers.ValidationError('Department must match subject department.')
        if subject and academic_year and subject.college_id != academic_year.college_id:
            raise serializers.ValidationError('Academic year must belong to the same college.')
        return attrs
